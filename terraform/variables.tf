variable "project_name" {
  description = "Name prefix for retail analytics resources."
  type        = string
  default     = "retail-analytics"
}

variable "location" {
  description = "Azure region for resources."
  type        = string
  default     = "eastus"
}

variable "environment" {
  description = "Deployment environment."
  type        = string
  default     = "dev"
}
