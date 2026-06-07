resource "azurerm_resource_group" "analytics" {
  name     = "${var.project_name}-${var.environment}-rg"
  location = var.location
}

resource "azurerm_storage_account" "data_lake" {
  name                     = replace("${var.project_name}${var.environment}sa", "-", "")
  resource_group_name      = azurerm_resource_group.analytics.name
  location                 = azurerm_resource_group.analytics.location
  account_tier             = "Standard"
  account_replication_type = "LRS"
  is_hns_enabled           = true
}
