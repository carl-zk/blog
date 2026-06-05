---
title: start with minikube
date: 2026-06-04 01:07:46
category:
tags:
---
## prepare
### ubuntu
```
➜  ~ cat /etc/os-release
PRETTY_NAME="Ubuntu 26.04 LTS"
NAME="Ubuntu"
VERSION_ID="26.04"
VERSION="26.04 LTS (Resolute Raccoon)"
VERSION_CODENAME=resolute
ID=ubuntu
ID_LIKE=debian
HOME_URL="https://www.ubuntu.com/"
SUPPORT_URL="https://help.ubuntu.com/"
BUG_REPORT_URL="https://bugs.launchpad.net/ubuntu/"
PRIVACY_POLICY_URL="https://www.ubuntu.com/legal/terms-and-policies/privacy-policy"
UBUNTU_CODENAME=resolute
LOGO=ubuntu-logo
➜  ~ lsb_release -a          
No LSB modules are available.
Distributor ID:	Ubuntu
Description:	Ubuntu 26.04 LTS
Release:	26.04
Codename:	resolute
➜  ~ hostnamectl                   
 Static hostname: fly
       Icon name: computer-desktop
         Chassis: desktop 🖥️
      Machine ID: 27599bc381e34ba291abba28a17da750
         Boot ID: 356f955395f14109bb5d122d99b027a6
Operating System: Ubuntu 26.04 LTS                
          Kernel: Linux 7.0.0-22-generic
    Architecture: x86-64
 Hardware Vendor: ASUS
  Hardware Model: ROG STRIX B760-G GAMING WIFI
    Hardware SKU: SKU
Hardware Version: System Version
Firmware Version: 0812
   Firmware Date: Mon 2023-02-27
    Firmware Age: 3y 3month 1w 
```
### docker 
> using docker for container runtime  
```
➜  ~ docker version
Client: Docker Engine - Community
 Version:           29.5.3
 API version:       1.54
 Go version:        go1.26.4
 Git commit:        d1c06ef
 Built:             Wed Jun  3 18:00:10 2026
 OS/Arch:           linux/amd64
 Context:           default

Server: Docker Engine - Community
 Engine:
  Version:          29.5.3
  API version:      1.54 (minimum version 1.40)
  Go version:       go1.26.4
  Git commit:       285b471
  Built:            Wed Jun  3 18:00:10 2026
  OS/Arch:          linux/amd64
  Experimental:     false
 containerd:
  Version:          v2.2.4
  GitCommit:        193637f7ee8ae5f5aa5248f49e7baa3e6164966e
 runc:
  Version:          1.3.5
  GitCommit:        v1.3.5-0-g488fc13e
 docker-init:
  Version:          0.19.0
  GitCommit:        de40ad0

```
或者 `docker info`
docker desktop 不是必要的.

#### docker proxy
```
➜  ~ docker info | grep -i proxy
 HTTP Proxy: http://127.0.0.1:10808
 HTTPS Proxy: http://127.0.0.1:10808
 No Proxy: localhost,127.0.0.1
  EnableUserlandProxy: true
  UserlandProxyPath: /usr/bin/docker-proxy

```

如果没有proxy, 就配置国内 docker镜像库。


## install 
> 本来配置的rootless docker, 后来发现遇到一些问题，最终还是换回default模式。学习kubtectl才是重点。
```sh
minikube delete --all

docker context use default

minikube start \
  --driver=docker \
  --container-runtime=containerd
或
minikube start \
  --driver=docker \
  --image-mirror-country=cn
```
设置 `alias kubectl="minikube kubectl --"`  

确保下面的info中没有异常，否则就执行`minikube delete --all`重新尝试其它方式。
```
➜  ~ kubectl describe node minikube
Name:               minikube
Roles:              control-plane
Labels:             beta.kubernetes.io/arch=amd64
                    beta.kubernetes.io/os=linux
                    kubernetes.io/arch=amd64
                    kubernetes.io/hostname=minikube
                    kubernetes.io/os=linux
                    minikube.k8s.io/commit=c93a4cb9311efc66b90d33ea03f75f2c4120e9b0
                    minikube.k8s.io/name=minikube
                    minikube.k8s.io/primary=true
                    minikube.k8s.io/updated_at=2026_06_05T12_07_43_0700
                    minikube.k8s.io/version=v1.38.1
                    node-role.kubernetes.io/control-plane=
                    node.kubernetes.io/exclude-from-external-load-balancers=
Annotations:        node.alpha.kubernetes.io/ttl: 0
                    volumes.kubernetes.io/controller-managed-attach-detach: true
CreationTimestamp:  Fri, 05 Jun 2026 12:07:31 +0800
Taints:             <none>
Unschedulable:      false
Lease:
  HolderIdentity:  minikube
  AcquireTime:     <unset>
  RenewTime:       Fri, 05 Jun 2026 12:51:25 +0800
Conditions:
  Type             Status  LastHeartbeatTime                 LastTransitionTime                Reason                       Message
  ----             ------  -----------------                 ------------------                ------                       -------
  MemoryPressure   False   Fri, 05 Jun 2026 12:49:31 +0800   Fri, 05 Jun 2026 12:07:30 +0800   KubeletHasSufficientMemory   kubelet has sufficient memory available
  DiskPressure     False   Fri, 05 Jun 2026 12:49:31 +0800   Fri, 05 Jun 2026 12:07:30 +0800   KubeletHasNoDiskPressure     kubelet has no disk pressure
  PIDPressure      False   Fri, 05 Jun 2026 12:49:31 +0800   Fri, 05 Jun 2026 12:07:30 +0800   KubeletHasSufficientPID      kubelet has sufficient PID available
  Ready            True    Fri, 05 Jun 2026 12:49:31 +0800   Fri, 05 Jun 2026 12:07:44 +0800   KubeletReady                 kubelet is posting ready status
Addresses:
  InternalIP:  192.168.49.2
  Hostname:    minikube
Capacity:
  cpu:                24
  ephemeral-storage:  1348412444Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             32138292Ki
  pods:               110
Allocatable:
  cpu:                24
  ephemeral-storage:  1348412444Ki
  hugepages-1Gi:      0
  hugepages-2Mi:      0
  memory:             32138292Ki
  pods:               110
System Info:
  Machine ID:                 86e0bfeb3f77427722393c2969964edb
  System UUID:                93f21ac7-2188-40d8-a2be-f752eb8da7fe
  Boot ID:                    356f9553-95f1-4109-bb5d-122d99b027a6
  Kernel Version:             7.0.0-22-generic
  OS Image:                   Debian GNU/Linux 12 (bookworm)
  Operating System:           linux
  Architecture:               amd64
  Container Runtime Version:  docker://29.2.1
  Kubelet Version:            v1.35.1
  Kube-Proxy Version:         
PodCIDR:                      10.244.0.0/24
PodCIDRs:                     10.244.0.0/24
Non-terminated Pods:          (7 in total)
  Namespace                   Name                                CPU Requests  CPU Limits  Memory Requests  Memory Limits  Age
  ---------                   ----                                ------------  ----------  ---------------  -------------  ---
  kube-system                 coredns-764897d7b-wcvfv             100m (0%)     0 (0%)      70Mi (0%)        170Mi (0%)     43m
  kube-system                 etcd-minikube                       100m (0%)     0 (0%)      100Mi (0%)       0 (0%)         43m
  kube-system                 kube-apiserver-minikube             250m (1%)     0 (0%)      0 (0%)           0 (0%)         43m
  kube-system                 kube-controller-manager-minikube    200m (0%)     0 (0%)      0 (0%)           0 (0%)         43m
  kube-system                 kube-proxy-bnrcp                    0 (0%)        0 (0%)      0 (0%)           0 (0%)         43m
  kube-system                 kube-scheduler-minikube             100m (0%)     0 (0%)      0 (0%)           0 (0%)         43m
  kube-system                 storage-provisioner                 0 (0%)        0 (0%)      0 (0%)           0 (0%)         43m
Allocated resources:
  (Total limits may be over 100 percent, i.e., overcommitted.)
  Resource           Requests    Limits
  --------           --------    ------
  cpu                750m (3%)   0 (0%)
  memory             170Mi (0%)  170Mi (0%)
  ephemeral-storage  0 (0%)      0 (0%)
  hugepages-1Gi      0 (0%)      0 (0%)
  hugepages-2Mi      0 (0%)      0 (0%)
Events:
  Type    Reason          Age   From             Message
  ----    ------          ----  ----             -------
  Normal  RegisteredNode  43m   node-controller  Node minikube event: Registered Node minikube in Controller
```

```
➜  ~ kubectl get pods -A           
NAMESPACE     NAME                               READY   STATUS    RESTARTS      AGE
kube-system   coredns-764897d7b-wcvfv            1/1     Running   0             47m
kube-system   etcd-minikube                      1/1     Running   0             48m
kube-system   kube-apiserver-minikube            1/1     Running   0             48m
kube-system   kube-controller-manager-minikube   1/1     Running   1             48m
kube-system   kube-proxy-bnrcp                   1/1     Running   0             47m
kube-system   kube-scheduler-minikube            1/1     Running   0             48m
kube-system   storage-provisioner                1/1     Running   1 (47m ago)   48m
```

## start nginx pod
### via proxy or not
由于没有配置minikube 使用宿主机代理，每次镜像拉取需要先docker pull, 再把镜像加载到minikube
```
docker pull nginx:latest
minikube image load nginx:latest
```
另一个方案是直接让minikube使用宿主机代理:  
假设你的宿主机 IP 是 192.168.1.100（不是 127.0.0.1）：  
确认代理对外监听（0.0.0.0 或宿主机局域网 IP）：  
`ss -tlnp | grep 10808`  
删除旧 Minikube：
`minikube delete`
重建 Minikube 并设置 docker 环境变量：  
```
minikube start \
  --driver=docker \
  --docker-env HTTP_PROXY=http://192.168.1.100:10808 \
  --docker-env HTTPS_PROXY=http://192.168.1.100:10808 \
  --docker-env NO_PROXY=localhost,127.0.0.1,192.168.49.2
```
这样 Minikube 内的 containerd 就能通过代理访问 Docker Hub。

nginx-pod.yaml
```
apiVersion: v1
kind: Pod
metadata:
  name: nginx-pod
  labels:
    app: nginx
spec:
  containers:
  - name: nginx-container
    image: nginx:latest
    imagePullPolicy: IfNotPresent # local image first
    ports:
    - containerPort: 80
```
因为latest标签的存在，kubelet默认取远程镜像。所以设置imagePullPolicy或指定版本。

`kubectl apply -f nginx-pod.yaml`

`kubectl port-forward nginx-pod 8080:80`

### help
#### check shell environment variables
```
➜  apt env | grep -i proxy          
ALL_PROXY=socks://127.0.0.1:10808
FTP_PROXY=ftp://127.0.0.1:10808
HTTPS_PROXY=http://127.0.0.1:10808
HTTP_PROXY=http://127.0.0.1:10808
NO_PROXY=localhost,127.0.0.0/8,::1
all_proxy=socks://127.0.0.1:10808
ftp_proxy=ftp://127.0.0.1:10808
http_proxy=http://127.0.0.1:10808
https_proxy=http://127.0.0.1:10808
no_proxy=localhost,127.0.0.0/8,::1

```
#### check current shell variables

```
➜  apt echo $http_proxy
echo $https_proxy
echo $HTTP_PROXY
echo $HTTPS_PROXY
echo $ALL_PROXY
http://127.0.0.1:10808
http://127.0.0.1:10808
http://127.0.0.1:10808
http://127.0.0.1:10808
socks://127.0.0.1:10808
```
#### check listening proxy processes
```
➜  apt ss -tlnp | grep -E "7890|1080|8080"
LISTEN 0      4096       127.0.0.1:10808      0.0.0.0:*    users:(("xray",pid=182024,fd=4))
```

#### where is proxy come from
```
➜  ~ gsettings get org.gnome.system.proxy mode
'manual'
➜  ~ gsettings list-recursively org.gnome.system.proxy
org.gnome.system.proxy autoconfig-url ''
org.gnome.system.proxy ignore-hosts ['localhost', '127.0.0.0/8', '::1']
org.gnome.system.proxy mode 'manual'
org.gnome.system.proxy use-same-proxy true
org.gnome.system.proxy.ftp host '127.0.0.1'
org.gnome.system.proxy.ftp port 10808
org.gnome.system.proxy.http authentication-password ''
org.gnome.system.proxy.http authentication-user ''
org.gnome.system.proxy.http enabled false
org.gnome.system.proxy.http host '127.0.0.1'
org.gnome.system.proxy.http port 10808
org.gnome.system.proxy.http use-authentication false
org.gnome.system.proxy.https host '127.0.0.1'
org.gnome.system.proxy.https port 10808
org.gnome.system.proxy.socks host '127.0.0.1'
org.gnome.system.proxy.socks port 10808

```

#### temporarily disable it from the terminal
`env -u http_proxy -u https_proxy -u HTTP_PROXY -u HTTPS_PROXY -u ALL_PROXY bash`