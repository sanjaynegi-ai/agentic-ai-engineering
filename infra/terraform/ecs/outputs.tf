output "application_url" { value = "http://${aws_lb.app.dns_name}" }
output "ecs_cluster" { value = aws_ecs_cluster.course.name }
output "ecs_service" { value = aws_ecs_service.app.name }
output "cloudwatch_log_group" { value = aws_cloudwatch_log_group.app.name }
output "cloudwatch_dashboard" { value = aws_cloudwatch_dashboard.app.dashboard_name }
output "target_group_arn" { value = aws_lb_target_group.app.arn }
