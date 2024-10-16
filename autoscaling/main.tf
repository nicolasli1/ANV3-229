# Creating our Week 21 VPC
resource "aws_vpc" "my-vpc-229" {
  cidr_block = "10.0.0.0/16"
}

# Creating our two subnets
resource "aws_subnet" "subnet-1" {
  vpc_id                  = aws_vpc.my-vpc-229.id
  cidr_block              = "10.0.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.project_name}-subnet-1"
  }
}

resource "aws_subnet" "subnet-2" {
  vpc_id                  = aws_vpc.my-vpc-229.id
  cidr_block              = "10.0.2.0/24"
  availability_zone       = "us-east-1b"
  map_public_ip_on_launch = true
  tags = {
    Name = "${var.project_name}-subnet-2"
  }
}

# Creating our internet gateway and attach it to the VPC
resource "aws_internet_gateway" "my-vpc-229-igw" {
  vpc_id = aws_vpc.my-vpc-229.id
  tags = {
    Name = "${var.project_name}-igw"
  }
}

resource "aws_route_table" "my-vpc-229-rt" {
  vpc_id = aws_vpc.my-vpc-229.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.my-vpc-229-igw.id
  }
  tags = {
    Name = "${var.project_name}-route-table"
  }
}

resource "aws_route_table_association" "awsrta-1" {
  subnet_id      = aws_subnet.subnet-1.id
  route_table_id = aws_route_table.my-vpc-229-rt.id
}

resource "aws_route_table_association" "awsrta-2" {
  subnet_id      = aws_subnet.subnet-2.id
  route_table_id = aws_route_table.my-vpc-229-rt.id
}

# Creating our security group that allows traffic from the internet
resource "aws_security_group" "allow-tls" {
  name        = "allow-tls"
  description = "Allow TLS and SSH inbound traffic from the internet"
  vpc_id      = aws_vpc.my-vpc-229.id

  # Regla para permitir tráfico HTTP en el puerto 80
  ingress {
    description = "HTTP from VPC"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = [aws_vpc.my-vpc-229.cidr_block]
  }

  # Regla para permitir tráfico SSH en el puerto 22
  ingress {
    description = "SSH from anywhere"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"] # Reemplaza con tu IP si prefieres restringir el acceso
  }

  # Regla de salida para permitir todo el tráfico
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "allow-tls"
  }
}


# Firewall configuration for the our instances
resource "aws_security_group_rule" "http-inbound" {
  type              = "ingress"
  from_port         = 80
  to_port           = 80
  protocol          = "tcp"
  cidr_blocks       = ["0.0.0.0/0"]
  security_group_id = aws_security_group.allow-tls.id
}

# Creating our launch configuration with user data to launch an Apache web server
resource "aws_launch_configuration" "lc" {
  name_prefix     = "${var.project_name}-lc"
  image_id        = "ami-06b21ccaeff8cd686"
  instance_type   = "t2.micro"
  security_groups = [aws_security_group.allow-tls.id]
  key_name        = "Nicolas-key2"
  user_data       = file("apache_httpd.sh")

  lifecycle {
    create_before_destroy = true
  }
}

# Creating our Auto Scaling group
resource "aws_autoscaling_group" "asg" {
  name = "${var.project_name}-asg"

  desired_capacity    = 4
  max_size            = 10
  min_size            = 2
  health_check_type   = "EC2"
  vpc_zone_identifier = [aws_subnet.subnet-1.id, aws_subnet.subnet-2.id]

  launch_configuration = aws_launch_configuration.lc.name
}


