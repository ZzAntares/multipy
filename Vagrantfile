
# the Vagrant development environment requires a box.
# steps for deploy
# 1 Download the box
# $ wget https://app.vagrantup.com/centos/boxes/7/versions/1804.02/providers/virtualbox.box
# 2 Add the box
# $ vagrant box add multipy/CentOS-7 CentOS-7-x86_64-Vagrant-1804_02.VirtualBox.box
# 3 Up box
# $ vagrant up multipy/CentOS-7
BOX_IMAGE = "multipy/CentOS-7"
NODE_COUNT = 2

Vagrant.configure("2") do |config|
  config.vm.define "master" do |subconfig|
    subconfig.vm.box = BOX_IMAGE
    subconfig.vm.hostname = "master"
    subconfig.vm.network :private_network, ip: "10.0.0.10"
  end

  (1..NODE_COUNT).each do |i|
    config.vm.define "node#{i}" do |subconfig|
      subconfig.vm.box = BOX_IMAGE
      subconfig.vm.hostname = "node#{i}"
      subconfig.vm.network :private_network, ip: "10.0.0.#{i + 10}"
    end
  end

  # Install avahi on all machines
  # Provisional comment because don't work <<provisional access to host is with the ip>>
    # config.vm.provision "shell", inline: <<-SHELL
    #  sudo rpm -ivh http://download.fedoraproject.org/pub/epel/6/x86_64/epel-release-6-8.noarch.rpm
    #  sudo yum install nss-mdns -y
    #  sudo service avahi-daemon start
    #  sudo yum install nano -y
    #  sudo yum install avahi-tools avahi-ui-tools -y
    # SHELL
    # Install python on all machines
      config.vm.provision "shell", inline: <<-SHELL
       sudo yum -y install nano wget
       sudo yum -y install gcc make kernel-headers kernel-devel perl
       sudo yum -y install yum-utils
       sudo yum -y install https://centos7.iuscommunity.org/ius-release.rpm
       sudo yum -y install python36u
       sudo yum -y install python36u-pip
       sudo yum -y install python36u-devel
       sudo yum -y groupinstall development
      SHELL
end