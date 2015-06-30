'use strict';

angular.module('app').config(['$stateProvider', '$urlRouterProvider',
    function ($stateProvider, $urlRouterProvider) {
        $urlRouterProvider
//        .when('/', '/cbos/pending/software/')
        .otherwise('/cbos/pending/software/');
        $stateProvider
            .state("layout", {
                url: "/",
                abstract: true,
                views:{
                    "":{
                        templateUrl: '/static/view/layout.html'
                    },
                    "sidebar@layout":{
                        templateUrl: '/static/view/sidebar.html'
                    }
                }
            })
            .state("layout.signout", {
                url: "signout/",
                template: '<div>退出中..</div>',
                controller: ["$scope", "$state", "$http", 'Auth', function($scope, $state, $http, Auth){
                    Auth.signout().then(function(){
                        $state.go("layout.signin");
                    });
                }]
            })
            .state("layout.home", {
                url: "",
                templateUrl: '/static/view/home.html',
                controller: ["$scope", "$state", function($scope, $state){
                    $state.go("layout.cdos.pending.software");
                }]
            })
            .state("layout.signin", {
                authenticated:false,
                url: "signin/",
                templateUrl: '/static/view/signin.html'
            })
            .state("layout.cdos", {
                url: "cbos/",
                abstract: true,
                template: "<div ui-view></div>"
            })
            .state("layout.cdos.pending", {
                url: "pending/",
                templateUrl: '/static/view/pending.html',
                abstract: true
            })

            .state("layout.cdos.pending.software", {
                url: "software/",
                authenticated:true,
                templateUrl: '/static/view/pending-software.html',
                controller: ["$scope", "$http", "$timeout", "$stateParams", "$state", "Resource", "$rootScope", function($scope, $http, $timeout, $stateParams, $state, Resource, $rootScope){
                    $scope.resource = new Resource("/cdos/api/v1/software/", {tag:"cdos-pending"}, 20);
                    $scope.refresh = function(){
                        var objects =  $.map($scope.resource.items, function(item){
                            return {
                                build_id: item["build_id"],
                                task_id: item["task_id"],
                                tag_name: item["tag_name"]
                            }
                        });
                        if(objects){
                            $http(
                            {
                                method: 'POST',
                                url: "/cdos/api/v1/software/refresh/",
                                data:{objects:objects},
                                noLoading:true
                            }).success(function(data){
                                var index = 0;
                                angular.forEach($scope.resource.items, function(item){
                                    var d = data[item.build_id];
                                    if(d["delete"]){
                                        $scope.resource.items.splice(index, 1);
                                    }else{
                                        index+=1;
                                    }
                                    angular.extend(item, d);
                                });
                                if($state.is("layout.cdos.pending.software"))
                                 $rootScope.timeoutRefresh = $timeout(function(){
                                   $scope.refresh()
                                 }, 3000);
                            })
                        }


                    };
                    $scope.resource.nextPage().then(function(){
                        if($state.is("layout.cdos.pending.software"))
                        $scope.refresh();
                    });

                    var update_progress = function(obj){
                        obj.progress+= 100/15.0/10;
                        if(obj.progress<100){
                            $timeout(function(){
                                update_progress(obj)
                            }, 100);
                        }else{
                            obj.loading = false;
                            $state.go('layout.cdos.stable.software');
                        }

                    };
                    $scope.test_pass = function(obj){
                        if(window.confirm("是否测试通过")){
                            obj.loading = true;
                            obj.progress = 0;
                            $http.post("/cdos/api/v1/software/pass/", obj).success(function(data){
                                if(!data.status){
                                    obj.loading = false;
                                    alert(data.msg||"error");
                                }else{
                                    update_progress(obj)
                                }
                            }).error(function(data){
                                console.log(data)
                                obj.loading = false;
                                alert(data.error_message||"error");
                            });
                        }
                    };

                }]
            })
            .state("layout.cdos.pending.image", {
                url: "image/",
                authenticated:true,
                templateUrl: '/static/view/pending-image.html',
                controller: ["$scope", "$http", "$state", "Resource", '$timeout', "$rootScope", "utils",
                    function($scope, $http, $state, Resource, $timeout, $rootScope, utils){
                    $scope.resource = new Resource("/cdos/api/v1/image/", {tag:"cdos-pending"}, 20);
                    $scope.resource.nextPage().then(function(){
                        if($state.is("layout.cdos.pending.image"))
                        $scope.refresh();
                    });
                    
                    $scope.refresh = function(){
                        var objects =  $.map($scope.resource.items, function(item){
                            return {
                                build_id: item["build_id"],
                                task_id: item["task_id"],
                                tag_name: item["tag_name"]
                            }
                        });
                        if(objects){
                            $http(
                            {
                                method: 'POST',
                                url: "/cdos/api/v1/image/refresh/",
                                data:{objects:objects},
                                noLoading:true
                            }).success(function(data){
                                angular.forEach($scope.resource.items, function(item){
                                    var d = data[item.build_id];
                                    angular.extend(item, d)
                                });
                                if($state.is("layout.cdos.pending.image"))
                                 $rootScope.timeoutRefresh = $timeout(function(){
                                   $scope.refresh()
                                 }, 3000)
                            })
                        }


                    };

                    var update_progress = function(obj){
                        obj.progress+= 100/15.0/10;
                        if(obj.progress<100){
                            $timeout(function(){
                                update_progress(obj)
                            }, 100);
                        }else{
                            obj.loading = false;
                            $state.go('layout.cdos.stable.software');
                        }

                    };
                    $scope.test_pass = function(obj){
                        if(window.confirm("是否测试通过")){
                            obj.loading = true;
                            obj.progress = 0;
                            $http.post("/cdos/api/v1/image/pass/", obj).success(function(data){
                                if(!data.status){
                                    obj.loading = false;
                                    alert(data.msg||"error");
                                }else{
                                    update_progress(obj);
                                }
                            });
                        }
                    }

                }]
            })

            .state("layout.cdos.stable", {
                url: "stable/",
                abstract: true,
                templateUrl: '/static/view/stable.html'
            })

            .state("layout.cdos.stable.software", {
                url: "software/",
                authenticated:true,
                templateUrl: '/static/view/stable-software.html',
                controller: ["$scope", "$http", "$stateParams", "$state", "Resource", function($scope, $http, $stateParams, $state, Resource){
                    $scope.resource = new Resource("/cdos/api/v1/software/", {tag:"cdos-stable"}, 20);
                    $scope.resource.nextPage();
                }]
            })
            .state("layout.cdos.stable.image", {
                url: "image/",
                authenticated:true,
                templateUrl: '/static/view/stable-image.html',
                controller: ["$scope", "$http", "Resource", function($scope, $http, Resource){
                    $scope.resource = new Resource("/cdos/api/v1/image/", {tag:"cdos-stable"}, 20);
                    $scope.resource.nextPage();
                    $scope.pxe = function(obj){
                        $http.post("/cdos/api/v1/image/pxe/", obj).success(function(data){
                            if(!data.status){
                                alert("error");
                            }
                            obj.loading = false;
                        });
                    }
                }]
            })
    }]);
