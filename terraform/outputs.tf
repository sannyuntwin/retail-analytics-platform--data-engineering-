output "resource_group_name" {
  value = azurerm_resource_group.analytics.name
}

output "storage_account_name" {
  value = azurerm_storage_account.data_lake.name
}
