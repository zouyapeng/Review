import json
import cbs
import os
import sys
import subprocess
from django.conf import settings


class CasApi(object):
    def __init__(self, cbs_url, home_dir):
        self.cbs_url = cbs_url
        self.home_dir = home_dir
        self.session = cbs.ClientSession(cbs_url)
        self.session.ssl_login(os.path.join(self.home_dir, ".cbs/client.crt"),
                               os.path.join(self.home_dir, ".cbs/clientca.crt"),
                               os.path.join(self.home_dir, ".cbs/serverca.crt"))

    def get_packages(self, tagid):
        builds = self.session.listTagged(tagid)
        return builds

    def get_images(self, tagid):
        #print tagid
        builds = self.session.listTagged(tagid, type='image')
        #print builds
        #builds = self.session.get_image_build_info(tagid)
        return builds

    def move_image(self, tag1, tag2, build):
        cmd = ['cbs', 'call', 'moveImageBuild', str(tag1), str(tag2), build]
        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = child.communicate() 
        print output
        if error:
            raise Exception(error)
        return output
    
    def move_package(self, tag1, tag2, build):
        pkgs = self.session.listPackages(tagID=tag2)
        nv = cbs.parse_NV(build)
        found = False
        for pkg in pkgs:
            if nv['name'] == pkg['package_name']:
                found = True
                break

        if found == False :
            self.session.packageListAdd(tag2, nv['name'], "cbsadmin")

        cmd = ['cbs', 'call', 'moveBuild', str(tag1), str(tag2), build]

        child = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        (output, error) = child.communicate()
        if error:
            raise Exception(error)
        self.session.newRepo("cdos-stable")
        return output
      


cas_api = CasApi(os.path.join(settings.CBS_URL, 'cbshub'), settings.HOME_DIR)

