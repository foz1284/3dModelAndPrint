@description('Location for all resources.')
param location string = resourceGroup().location

@description('Name of the App Service plan.')
param appServicePlanName string = 'asp-3dmodelandprint'

@description('Name of the web app.')
param webAppName string = 'app-3dmodelandprint-${uniqueString(resourceGroup().id)}'

resource plan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: appServicePlanName
  location: location
  kind: 'linux'
  sku: {
    name: 'B1'
    tier: 'Basic'
  }
  properties: {
    reserved: true
  }
}

resource webApp 'Microsoft.Web/sites@2023-01-01' = {
  name: webAppName
  location: location
  kind: 'app,linux'
  properties: {
    serverFarmId: plan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'NODE|20-lts'
      alwaysOn: true
      ftpsState: 'FtpsOnly'
      appSettings: [
        {
          name: 'WEBSITE_RUN_FROM_PACKAGE'
          value: '1'
        }
      ]
    }
  }
}

output webAppUrl string = 'https://${webApp.properties.defaultHostName}'
