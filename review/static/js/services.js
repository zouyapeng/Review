
'use strict';
angular.module('myApp.services', [])
    .factory('utils', [function () {
        return {
            findById: function findById(a, id) {
                for (var i = 0; i < a.length; i++) {
                    if (a[i].id == id) return a[i];
                }
                return null;
            },
            newRandomKey: function newRandomKey(coll, key, currentKey){
                var randKey;
                do {
                    randKey = coll[Math.floor(coll.length * Math.random())][key];
                } while (randKey == currentKey);
                return randKey;
            },
            getSelect:function(objs,status){
                var status = status?status:true;
                return $.grep(objs,function(v){
                    return v.isSelected == status;
                })
            },
            dictGrep:function(dict,fun,filter){
                var args = {};
                angular.forEach(dict, function (v, k) {
                    if(!filter || ($.inArray(k,filter)!=-1)){
                        if(fun){
                            if(fun(v,k)){
                                args[k] = v;
                            }
                        }else{
                            if (v && v != 'null') {
                                args[k] = v;
                            }
                        }
                    }

                })
                return args;
            }

        }
    }])
    .factory('Resource', ['$http', '$q',function($http, $q) {
        var Resource = function(url,args,limit) {
            this.items = [];
            this.busy = false;
            this.offset = 0;
            this.start = 0;
            this.next = null;
            this.limit = limit||20;
            this.total_count = -1;
            this.url = url;
            this.args = args
        };

        Resource.prototype.request = function(args) {
            return $http.get(this.url,{params: args});
        }
        Resource.prototype.refresh = function() {
            this.items = [];
            this.busy = false;
            this.offset = 0;
            this.nextPage(true);
        }
        Resource.prototype.goPage = function(clear, page) {
            var args = angular.copy(this.args);
            args['offset'] = (page-1)*this.limit;
            this.request(args, clear, page).success(function(data){
                this.total_count = data.meta.total_count;
                if(clear){
                    this.items = data.objects;
                }else{
                    angular.forEach(data.objects,function(item){
                        self.items.push(item);
                    });
                };
                this.offset = page*this.limit;
                this.start = args['offset'];
            }.bind(this));

        }

        Resource.prototype.nextPage = function(clear) {
             
            var defer = $q.defer();
            if (this.busy||(this.total_count!=-1&&this.offset>=this.total_count)) return;
            this.busy = true;
            var args = angular.copy(this.args);
            args['offset'] = this.offset;
            args['limit'] = this.limit;
            $http.get(this.url,{params: args}).success(function(data) {
                this.total_count = data.meta.total_count;
                var self = this;
                if(clear){
                    self.items = data.objects;
                    this.offset=this.limit;
                }else{
                    angular.forEach(data.objects,function(item){
                        self.items.push(item);
                    });
                    this.offset+=this.limit;
                }

                this.next=data.meta.next;
                this.busy = false;
                
                defer.resolve();
            }.bind(this));
            
            return defer.promise;
        };

        return Resource;
    }])
    .factory('alertService', ["$rootScope", "$timeout", function($rootScope, $timeout) {
        var alertService = {};
        $rootScope.alerts = [];
        return {
            add: function(type, msg){
                var alert = {'type': type, 'msg': msg };
                $rootScope.alerts.push(alert);
                $timeout(function(){
//                    $rootScope.alerts.splice($rootScope.alerts.indexOf(alert), 1);
                }, 2000)
            }
        };
    }])
    .factory('Auth',['$http','$q','$timeout',function($http,$q,$timeout){
        return {
            user: {},
            authenticated: false,
            init:function(){
                var self = this;
                var defer = $q.defer();
                $http.get('/cdos/api/v1/user/').success(function(data){
                     if(data.authenticated){
                        angular.extend(self.user, data);
                        self.authenticated = true;
                        defer.resolve();
                     }else{
                        defer.reject();
                     }
                });
                return defer.promise;
            },
            signout: function(){
                var self = this;
                var defer = $q.defer();
                return $http.get("/cdos/api/v1/user/signout/").success(function(){
                    self.authenticated = false;
                    self.user = {};
                    defer.resolve();
                }).error(function(){
                    defer.reject();
                });
                return defer.promise;
            }
        }
    }]);
