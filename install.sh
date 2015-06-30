#!/bin/bash

#本脚本需要root身份执行 或者 sudo ./update.sh 执行

[ `id -u` = 0 ] || exit 0
#now_date=`date`

#echo $now_date > install.log
#安装nginx
echo "Start the installation of nginx..."
apt-get -y install nginx
if [ $? != 0 ]; then
    echo "========================================"
    echo "Can not install nginx, then exit"
    exit 2
else
    echo "Complete the installation of nginx"
fi
#安装依赖
echo "Start the installation of python-dev..."
apt-get -y install python-dev
if [ $? != 0 ]; then
    echo "========================================"
    echo "can not install python-dev, then exit"
    exit 2
else
    echo "Complete the installation of python-dev"
fi


echo "Start the installation of python-pip..."
apt-get -y install python-pip
if [ $? != 0 ]; then
    echo "========================================"
    echo "can not install python-pip, then exit"
    exit 2
else
    echo "Complete the installation of python-pip"
fi

echo "Start the installation of cbs..."
apt-get -y install python-urlgrabber python-krbv
if [ $? != 0 ]; then
    echo "========================================"
    echo "can not install python-urlgrabber python-krbv, then exit"
    exit 2
else
    echo "Complete the installation of python-urlgrabber python-krbv"
fi

dpkg -i ./cbs_0.1.3_all.deb 


#安装python依赖模块
PACKAGES_PATH="./requirements_packages/"
for package in `ls ./requirements_packages/`;do
    echo "Installing '$package'..."
    easy_install $PACKAGES_PATH/$package
    
    if [ $? != 0 ]; then
        echo "========================================"
        echo "can not install '$package', then exit"
        exit 2
    fi
    
    done



#拷贝配置文件
rm -rf /etc/nginx/sites-enabled/default
mkdir -p /var/www
cp -rf ./review/ /var/www/
cp ./config/review_http /etc/nginx/sites-enabled/
cp ./config/review_start.sh /etc/profile.d/
cp -rf ./config/.cbs /home/cas/

chown www-data:www-data /var/www/review  -R

#重启服务
uwsgi --ini ./review/uwsgi.ini
service nginx restart


