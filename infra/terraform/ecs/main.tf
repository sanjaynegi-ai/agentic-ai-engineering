locals {
  # Keep generated AWS names short and collision-resistant. Long project selectors
  # otherwise collide when load-balancer names are truncated to 32 characters.
  resource_name = "${substr(replace(var.project_name, "_", "-"), 0, 22)}-${substr(md5(var.project_name), 0, 8)}"
}

resource "aws_cloudwatch_log_group" "app" {
  name              = "/ecs/agentic-ai/${local.resource_name}"
  retention_in_days = 14
}
resource "aws_ecs_cluster" "course" {
  name = "agentic-ai-${local.resource_name}"
  setting {
    name  = "containerInsights"
    value = "enabled"
  }
}
resource "aws_iam_role" "execution" {
  name               = "agentic-ai-${local.resource_name}-execution"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_iam_role_policy_attachment" "execution" {
  role       = aws_iam_role.execution.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy"
}
resource "aws_iam_role_policy" "secret" {
  role   = aws_iam_role.execution.id
  policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Action = ["secretsmanager:GetSecretValue"], Resource = var.openai_secret_arn }] })
}
resource "aws_iam_role" "task" {
  name               = "agentic-ai-${local.resource_name}-task"
  assume_role_policy = jsonencode({ Version = "2012-10-17", Statement = [{ Effect = "Allow", Principal = { Service = "ecs-tasks.amazonaws.com" }, Action = "sts:AssumeRole" }] })
}
resource "aws_security_group" "alb" {
  name   = "agentic-ai-${local.resource_name}-alb"
  vpc_id = var.vpc_id
  ingress {
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_security_group" "app" {
  name   = "agentic-ai-${local.resource_name}-app"
  vpc_id = var.vpc_id
  ingress {
    from_port       = 7860
    to_port         = 7860
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}
resource "aws_lb" "app" {
  name               = local.resource_name
  load_balancer_type = "application"
  subnets            = var.public_subnet_ids
  security_groups    = [aws_security_group.alb.id]
}
resource "aws_lb_target_group" "app" {
  name        = local.resource_name
  port        = 7860
  protocol    = "HTTP"
  target_type = "ip"
  vpc_id      = var.vpc_id
  health_check { path = "/" }
}
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.app.arn
  port              = 80
  protocol          = "HTTP"
  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.app.arn
  }
}
resource "aws_ecs_task_definition" "app" {
  family                   = local.resource_name
  network_mode             = "awsvpc"
  requires_compatibilities = ["FARGATE"]
  cpu                      = "512"
  memory                   = "1024"
  execution_role_arn       = aws_iam_role.execution.arn
  task_role_arn            = aws_iam_role.task.arn
  container_definitions    = jsonencode([{ name = "app", image = var.image_uri, essential = true, portMappings = [{ containerPort = 7860, protocol = "tcp" }], secrets = [{ name = "OPENAI_API_KEY", valueFrom = var.openai_secret_arn }], logConfiguration = { logDriver = "awslogs", options = { "awslogs-group" = aws_cloudwatch_log_group.app.name, "awslogs-region" = var.aws_region, "awslogs-stream-prefix" = "app" } } }])
}
resource "aws_ecs_service" "app" {
  name            = local.resource_name
  cluster         = aws_ecs_cluster.course.id
  task_definition = aws_ecs_task_definition.app.arn
  desired_count   = 1
  launch_type     = "FARGATE"
  network_configuration {
    subnets          = var.public_subnet_ids
    security_groups  = [aws_security_group.app.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.app.arn
    container_name   = "app"
    container_port   = 7860
  }
  depends_on = [aws_lb_listener.http]
}

resource "aws_cloudwatch_metric_alarm" "ecs_cpu_high" {
  alarm_name          = "${local.resource_name}-ecs-cpu-high"
  alarm_description   = "ECS service CPU has exceeded 80 percent for 10 minutes."
  namespace           = "AWS/ECS"
  metric_name         = "CPUUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  dimensions = {
    ClusterName = aws_ecs_cluster.course.name
    ServiceName = aws_ecs_service.app.name
  }
}

resource "aws_cloudwatch_metric_alarm" "ecs_memory_high" {
  alarm_name          = "${local.resource_name}-ecs-memory-high"
  alarm_description   = "ECS service memory has exceeded 80 percent for 10 minutes."
  namespace           = "AWS/ECS"
  metric_name         = "MemoryUtilization"
  statistic           = "Average"
  period              = 300
  evaluation_periods  = 2
  threshold           = 80
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "notBreaching"
  dimensions = {
    ClusterName = aws_ecs_cluster.course.name
    ServiceName = aws_ecs_service.app.name
  }
}

resource "aws_cloudwatch_metric_alarm" "alb_unhealthy_targets" {
  alarm_name          = "${local.resource_name}-unhealthy-targets"
  alarm_description   = "The load balancer has one or more unhealthy application targets."
  namespace           = "AWS/ApplicationELB"
  metric_name         = "UnHealthyHostCount"
  statistic           = "Maximum"
  period              = 60
  evaluation_periods  = 2
  threshold           = 0
  comparison_operator = "GreaterThanThreshold"
  treat_missing_data  = "breaching"
  dimensions = {
    LoadBalancer = aws_lb.app.arn_suffix
    TargetGroup  = aws_lb_target_group.app.arn_suffix
  }
}

resource "aws_cloudwatch_dashboard" "app" {
  dashboard_name = "agentic-ai-${local.resource_name}"
  dashboard_body = jsonencode({
    widgets = [
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "ECS CPU and memory"
          region = var.aws_region
          view   = "timeSeries"
          metrics = [
            ["AWS/ECS", "CPUUtilization", "ClusterName", aws_ecs_cluster.course.name, "ServiceName", aws_ecs_service.app.name],
            [".", "MemoryUtilization", ".", ".", ".", "."]
          ]
        }
      },
      {
        type   = "metric"
        width  = 12
        height = 6
        properties = {
          title  = "Load balancer health and latency"
          region = var.aws_region
          view   = "timeSeries"
          metrics = [
            ["AWS/ApplicationELB", "TargetResponseTime", "LoadBalancer", aws_lb.app.arn_suffix, "TargetGroup", aws_lb_target_group.app.arn_suffix],
            [".", "HTTPCode_Target_5XX_Count", ".", ".", ".", ".", { stat = "Sum" }],
            [".", "UnHealthyHostCount", ".", ".", ".", ".", { stat = "Maximum" }]
          ]
        }
      },
      {
        type   = "log"
        width  = 24
        height = 6
        properties = {
          title  = "Recent application errors"
          region = var.aws_region
          query  = "SOURCE '${aws_cloudwatch_log_group.app.name}' | fields @timestamp, @message | filter @message like /ERROR|Exception|Traceback/ | sort @timestamp desc | limit 50"
        }
      }
    ]
  })
}
