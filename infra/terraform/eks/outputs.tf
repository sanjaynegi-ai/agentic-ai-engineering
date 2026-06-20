output "load_balancer_hostname" { value = try(kubernetes_service_v1.app.status[0].load_balancer[0].ingress[0].hostname, null) }
