@description('Nombre de la máquina virtual')
param vmName string

@description('Nombre de usuario administrador')
param adminUsername string

@description('Clave pública SSH')
param publicKey string

@description('Ubicación de la VM')
param location string = resourceGroup().location

@description('Tamaño de la VM')
param vmSize string = 'Standard_B1s'  // Tamaño dentro de la capa gratuita

@description('Imagen de la VM')
param imagePublisher string = 'Canonical'
@description('Imagen de la VM')
param imageOffer string = 'UbuntuServer'
@description('Imagen de la VM')
param imageSku string = '22.04-LTS-gen2'  // SKU para Ubuntu 22.04 LTS Gen 2

param vnetName string = 'mi-vnet'
param subnetName string = 'default'
param addressPrefix string = '10.0.0.0/16'
param subnetPrefix string = '10.0.0.0/24'

resource vnet 'Microsoft.Network/virtualNetworks@2021-02-01' = {
  name: vnetName
  location: location
  properties: {
    addressSpace: {
      addressPrefixes: [
        addressPrefix
      ]
    }
    subnets: [
      {
        name: subnetName
        properties: {
          addressPrefix: subnetPrefix
        }
      }
    ]
  }
}

resource pip 'Microsoft.Network/publicIPAddresses@2021-02-01' = {
  name: '${vmName}PIP'
  location: location
  properties: {
    publicIPAllocationMethod: 'Dynamic'
  }
}

resource ni 'Microsoft.Network/networkInterfaces@2021-02-01' = {
  name: '${vmName}NIC'
  location: location
  properties: {
    ipConfigurations: [
      {
        name: 'ipconfig1'
        properties: {
          subnet: {
            id: '${vnet.id}/subnets/${subnetName}'
          }
          publicIPAddress: {
            id: pip.id
          }
        }
      }
    ]
  }
}

resource vm 'Microsoft.Compute/virtualMachines@2021-03-01' = {
  name: vmName
  location: location
  properties: {
    hardwareProfile: {
      vmSize: vmSize
    }
    storageProfile: {
      imageReference: {
        publisher: imagePublisher
        offer: imageOffer
        sku: imageSku
        version: 'latest'
      }
      osDisk: {
        createOption: 'FromImage'
      }
    }
    osProfile: {
      computerName: vmName
      adminUsername: adminUsername
      linuxConfiguration: {
        disablePasswordAuthentication: true
        ssh: {
          publicKeys: [
            {
              path: '/home/${adminUsername}/.ssh/authorized_keys'
              keyData: publicKey
            }
          ]
        }
      }
    }
    networkProfile: {
      networkInterfaces: [
        {
          id: ni.id
        }
      ]
    }
  }
}



// DESPLIEGUE
// az group create --name nombre-de-tu-grupo-de-recursos --location eastus
// az deployment group create --resource-group nombre-de-tu-grupo-de-recursos --template-file main.bicep --parameters @parameters.json
// ssh -i vm mi-usuario@13.67.165.82
// az group delete --name nombre-de-tu-grupo-de-recursos --yes --no-wait

