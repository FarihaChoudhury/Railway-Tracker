variable "AWS_ACCESS_KEY" {
  type = string
}
variable "AWS_SECRET_KEY" {
  type = string
}
variable "AWS_REGION" {
    type = string
    default = "eu-west-2"
}

variable "C11_VPC"{
    type = string
}


variable "DB_USERNAME" {
    type = string
}
variable "DB_PASSWORD"{
    type = string
}
variable "DB_NAME" {
    type = string
}
variable "DB_IP"{
    type = string
}
variable "DB_PORT"{
    type = string
}


variable "REALTIME_USERNAME" {
    type = string
}
variable "REALTIME_PASSWORD"{
    type = string
}


variable "NATIONAL_RAIL_API_KEY" {
    type = string
}

variable "SOURCE_EMAIL" {
    type = string
}
variable "S3_BUCKET_NAME" {
    type = string
}