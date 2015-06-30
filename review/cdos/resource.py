# # -*- coding: utf-8 -*-
from django.contrib.admin.models import LogEntry
from django.contrib.contenttypes.models import ContentType
from django.utils.encoding import force_unicode
import os
from random import random
from django.conf import settings
from django.conf.urls import url
import subprocess
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
from django.core.urlresolvers import reverse
from django.shortcuts import redirect

import requests
from tastypie.authentication import SessionAuthentication
from tastypie.authorization import DjangoAuthorization
from tastypie.resources import Resource, NamespacedModelResource
from tastypie.utils import trailing_slash, now
import time
from cdos.client import Client
import getPackages


class UserResource(NamespacedModelResource):
    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/signin%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('signin'), name='signin_api'),
            url(r"^(?P<resource_name>%s)/signout%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('signout'), name='signout_api'),
        ]

    def signout(self, request, **kwargs):
        logout(request)
        request.session["user_type"] = None
        return self.create_response(request, {})

    def signin(self, request, **kwargs):
        code = request.GET['code']
        client = Client(settings.CAS_SETTINGS["client_id"],
                        settings.CAS_SETTINGS["client_secret"],
                        settings.SIGNIN_BACK,
                        settings.CAS_SETTINGS["authorization_uri"],
                        settings.CAS_SETTINGS["token_uri"],
                        settings.CAS_SETTINGS["openid_uri"],
                        settings.CAS_SETTINGS["user_api_uri"])
        openid = None
        try:
            token = client.get_token(code=code)
            error = token.get('error')
            if error:
                token = None
            else:
                # 获取openid
                openid = client.get_openid(token['access_token'])['openid']
        except Exception as e:
            print e

        if openid:
            access_token = token["access_token"]
            user_info = client.get_user_info(access_token, openid)
            try:
                User.objects.get(id=openid)
            except ObjectDoesNotExist:
                # 创建新的用户
                user_info = client.get_user_info(access_token, openid)
                User.objects.create_user(user_info["username"], user_info.get("email"), id=openid)
            user = authenticate(openid=openid)
            if user:
                login(request, user)
                try:
                    self.get_user_group_info(request, client, access_token)
                except Exception as e:
                    pass

                return redirect(reverse("home"))

    def get_user_group_info(self, request, client, access_token):
        group_info = client.get_user_group_info(access_token, request.user.id)
        request.session["user_type"] = None
        if group_info.get("is_active"):
            request.session["user_type"] = group_info['user_type']

    def get_list(self, request, **kwargs):
        if not request.user.is_authenticated():
            return self.create_response(request, {"authenticated": False})
        obj = super(UserResource, self).get_object_list(request).get(id=request.user.id)
        bundle = self.build_bundle(obj=obj, request=request)
        bundle = self.full_dehydrate(bundle, for_list=True)
        return self.create_response(request, bundle)

    def dehydrate(self, bundle):
        bundle.data["authenticated"] = True
        bundle.data["user_type"] = bundle.request.session.get("user_type")
        return bundle

    def get_object_list(self, request):
        objects = super(UserResource, self).get_object_list(request).filter(id=request.user.id)
        return objects

    class Meta:
        queryset = User.objects.filter(pk__gt=0)
        fields = ['id', 'username']
        resource_name = 'user'
        # authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        list_allowed_methods = ['get']
        detail_allowed_methods = ['get']


class CbsResource(Resource):
    def get_status_by_task_id(self, _type, task_id):
        try:
            r = requests.get("http://172.29.10.101:8000/autotest/%s/?task_id=%s" % (_type, task_id), timeout=2)
            r_data = r.json()
            return r_data["status"]
        except Exception as e:
            print e
            return "pending"

    def full_dehydrate(self, bundle, for_list=False):
        bundle.data = bundle.obj
        bundle = self.dehydrate(bundle)
        return bundle


class SoftwareResource(CbsResource):
    def obj_get_list(self, bundle, **kwargs):
        packages = getPackages.cas_api.get_packages(bundle.request.GET.get("tag"))
        # print getPackages.cas_api.move_package(5, 3, "hellodemo_1.2")

        return packages

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/pass%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('test_pass'), name='test_pass'),

            url(r"^(?P<resource_name>%s)/refresh%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('refresh'), name='refresh'),
        ]

    def test_pass(self, request, **kwargs):
        if not request.session.get("user_type"):
            return self.create_response(request, {"status": False, "msg": "无权限"})


        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        if data['status'] != "finished":
            return self.create_response(request, {"status": False, "msg": "status error"})
        try:
            task_id = getPackages.cas_api.move_package(data["tag_id"], 5, data["nvr"])
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(request.user).pk,
                object_id=request.user.pk,
                object_repr=force_unicode(request.user),
                action_flag=2,
                change_message="测试通过：move_package {f_tag_id} {t_tag_id} {nvr}".format(nvr=data["nvr"],
                                                                                      f_tag_id=data["tag_id"],
                                                                                      t_tag_id=5)
            )
        except Exception as e:
            return self.create_response(request, {"status": False, "msg": str(e)})
        return self.create_response(request, {"status": True})

    def refresh(self, request, **kwargs):
        self.method_check(request, allowed=['post'])
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        objects = {}
        for obj in data["objects"]:
            build_id = obj["build_id"]
            obj_data = {"status": 'invalid'}
            if obj.get("task_id"):
                # 获取状态
                obj_data["status"] = self.get_status_by_task_id("packagetest", obj.get("task_id"))
            objects[build_id] = obj_data
        return self.create_response(request, objects)

    def dehydrate(self, bundle):
        # if bundle.request.GET.get("tag") == "cdos-pending":
        # bundle.data["status"] = "pending"
        #     if bundle.data.get("task_id"):
        #         bundle.data["status"] = self.get_status_by_task_id("packagetest", bundle.data["task_id"])
        return bundle

    class Meta:
        resource_name = 'software'
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        limit = 20


class ImageResource(CbsResource):
    def obj_get_list(self, bundle, **kwargs):
        packages = getPackages.cas_api.get_images(bundle.request.GET.get("tag"))
        # packages = getPackages.cas_api.get_packages("cdos")
        return packages

    def prepend_urls(self):
        return [
            url(r"^(?P<resource_name>%s)/pass%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('test_pass'), name='test_pass'),
            url(r"^(?P<resource_name>%s)/pxe%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('images_pxe'), name='images_pxe'),
            url(r"^(?P<resource_name>%s)/refresh%s$" % (self._meta.resource_name, trailing_slash()),
                self.wrap_view('refresh'), name='refresh'),
        ]

    def images_pxe(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        if not request.session.get("user_type"):
            return self.create_response(request, {"status": False, "msg": "无权限"})
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        filename = data["image_name"] + "-" + data["version"] + "-" + data["arch"] + ".iso"
        filename_path = os.path.join(settings.CBS_URL, "cbsfiles/release/cdos-stable", filename)

        cmd = ['ssh', settings.PXE, 'auto_deploy_iso_to_pxe', filename_path]

        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        (output, error) = child.communicate()
        # if error:
        #     return self.create_response(request, {"status": False, "error": error})

        LogEntry.objects.log_action(
            user_id=request.user.pk,
            content_type_id=ContentType.objects.get_for_model(request.user).pk,
            object_id=request.user.pk,
            object_repr=force_unicode(request.user),
            action_flag=2,
            change_message="PXE：{filename}".format(filename=filename)
        )

        return self.create_response(request, {"status": True})

    def test_pass(self, request, **kwargs):
        self.method_check(request, allowed=['post'])

        if not request.session.get("user_type"):
            return self.create_response(request, {"status": False, "msg": "无权限"})
        self.is_authenticated(request)
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))

        if data['status'] != "finished":
            return self.create_response(request, {"status": False, "msg": "status error"})
        try:
            image_name = "%s_%s_%s" % (data["image_name"], data["version"], data["arch"])
            task_id = getPackages.cas_api.move_image(data["tag_id"], 5, image_name)

            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(request.user).pk,
                object_id=request.user.pk,
                object_repr=force_unicode(request.user),
                action_flag=2,
                change_message="测试通过：move_image {f_tag_id} {t_tag_id} {image_name}".format(image_name=image_name,
                                                                                           f_tag_id=data["tag_id"],
                                                                                           t_tag_id=5)
            )
        except Exception as e:
            print e
            return self.create_response(request, {"status": False, "msg": str(e)})
        return self.create_response(request, {"status": True})

    def refresh(self, request, **kwargs):
        data = self.deserialize(request, request.body,
                                format=request.META.get('CONTENT_TYPE', 'application/json'))
        objects = {}
        for obj in data["objects"]:
            build_id = obj["build_id"]
            obj_data = {}
            if obj.get("task_id"):
                # 获取状态
                obj_data["status"] = self.get_status_by_task_id("systemtest", obj.get("task_id"))
            objects[build_id] = obj_data
        return self.create_response(request, objects)

    def dehydrate(self, bundle):
        # if bundle.request.GET.get("tag") == "cdos-pending":
        # bundle.data["status"] = "pending"
        #     if bundle.data.get("task_id"):
        #         bundle.data["status"] = self.get_status_by_task_id("systemtest", bundle.data["task_id"])
        return bundle

    class Meta:
        resource_name = 'image'
        authentication = SessionAuthentication()
        authorization = DjangoAuthorization()
        limit = 20
