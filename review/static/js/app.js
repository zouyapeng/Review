
'use strict';
angular.module('HashBangURLs', []).config(['$locationProvider', function($location) {
//  $location.hashPrefix('!');
}]);

var app = angular.module('app',['HashBangURLs', 'ui.bootstrap','ui.router',
    "angular-loading-bar", 'ngAnimate','ngSanitize', 'myApp.services'
]).config(['$httpProvider','$interpolateProvider','$locationProvider', "cfpLoadingBarProvider",
        function ($httpProvider, $interpolateProvider, $locationProvider, cfpLoadingBarProvider) {
        cfpLoadingBarProvider.includeSpinner = true;
        $locationProvider.html5Mode(true);
        $interpolateProvider.startSymbol('{[');
        $interpolateProvider.endSymbol(']}');
        $httpProvider.defaults.xsrfCookieName = 'csrftoken';
        $httpProvider.defaults.xsrfHeaderName = 'X-CSRFToken';
    }])
.run(['$rootScope', '$http', '$state', '$stateParams','utils','Auth','$injector', "$timeout",
        function ($rootScope, $http, $state, $stateParams,utils,Auth,$injector, $timeout) {
                $rootScope.$on('$stateChangeStart', function(event, toState, toParams, fromState, fromParams){
                    $timeout.cancel($rootScope.timeoutRefresh);
                    if(toState.authenticated){
                        if (!Auth.authenticated) {
                            event.preventDefault();
                            Auth.init().then(function () {
                                $state.go(toState, toParams);
                            }, function () {
                                $state.go('layout.signin');
                            });
                        } else {
                            $rootScope.auth = Auth;
                        }
                    }
                })
        }]);




angular.module("template/pagination/pagination.html", []).run(["$templateCache", function($templateCache) {
  $templateCache.put("template/pagination/pagination.html",
    "<ul class=\"pagination\">\n" +
    "  <li ng-if=\"boundaryLinks\" ng-class=\"{disabled: noPrevious()}\"><a href ng-click=\"selectPage(1)\">第一页</a></li>\n" +
    "  <li ng-if=\"directionLinks\" ng-class=\"{disabled: noPrevious()}\"><a href ng-click=\"selectPage(page - 1)\">上一页</a></li>\n" +
    "  <li ng-repeat=\"page in pages track by $index\" ng-class=\"{active: page.active}\"><a href ng-click=\"selectPage(page.number)\">{{page.text}}</a></li>\n" +
    "  <li ng-if=\"directionLinks\" ng-class=\"{disabled: noNext()}\"><a href ng-click=\"selectPage(page + 1)\">下一页</a></li>\n" +
    "  <li ng-if=\"boundaryLinks\" ng-class=\"{disabled: noNext()}\"><a href ng-click=\"selectPage(totalPages)\">最后一页</a></li>\n" +
    "</ul>");
}]);
