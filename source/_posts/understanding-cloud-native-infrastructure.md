---
title: understanding cloud-native infrastructure
date: 2026-05-30 20:36:22
category:
tags:
    - cloud-native
    - linux-kernal
    - namespace
---
> since I want to know what's cloud-native and why it is the future, this is how I learn.

## Roadmap
### Container fundamentals

**Linux fundamentals**
```
namespace
cgroups
process isolation
virtual networking
iptables/ipvs
overlay filesystem
```

**Docker/containerd**
```
image layering
OCI runtime
container networking
bridge/veth
volume mounting
```

### Kubernetes core architecture

**Control Plane**
- kube-apiserver  
    The center of everything.  
- etcd  
    Distributed state storage.  
- scheduler  
    How pods get assigned to nodes.  
- controller-manager  
    Why Kubernetes is declarative.  

**Node side**  
- kubelet  
    Actual node agent.  
- container runtime  
    Usually containerd.  
- kube-proxy  
    Networking + Service implementation.  

### Networking
- service  
    how service discovery works.
- coreDNS  
    how dns resolution works.  
- kube-proxy  
    iptables vs ipvs.  
- CNI ()    
- Ingress / Gateway API  
    North-sourth traffic.  
- Service Mesh basics  

### Storage
- PersistenVolume
- CSI drivers
- StatefulSet
- Distributed storage concepts

### Observability
- Metrics  
    Prometheus  
- Logging  
    Loki / ELK  
- Tracing  
    OpenTelemetry  

### GitOps
Argo CD

### Service Mesh
**Envoy**  

**Istio**  
- sidecar injection
- xDS
- traffic management
- mTLS
- retries
- canary routing

### Platform engineering
```
internal Developer Platform  
automation
templates
operators
self-service
```

after all previous stages, the biggest mindset change you get is  
Traditional Java backend mindset: `Application-centric`  
Cloud-native mindset: `Platform-centric`  
Meaning:
- applications are disposable
- infrastructure becomes programmable
- reconciliation replaces imperative operations
- networking becomes software-defined

This shift is much bigger than simply "learning Kubernetes".  
`Kubernetes is a distributed control system, NOT a container deployment tool.`