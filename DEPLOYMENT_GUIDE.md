# STRIDE + Momento Deployment Guide

## Overview

This guide provides step-by-step instructions for deploying the STRIDE + Momento integration in two environments:

1. Cloud Deployment (Recommended for production)
2. Debian VM on Azure (For development/testing)

---

## Prerequisites

### 1. Required Accounts & Keys
| Service | Purpose | How to Get |
|---------|---------|------------|
| GitHub | Code repository | [Sign Up](https://github.com/) |
| Momento | Caching platform | [Sign Up](https://console.gomomento.com/) |
| Google Cloud (Gemini API) | Teacher LLM (Gemini-3.1-Pro) | [Get API Key](https://ai.google.dev/) |
| Azure | Cloud deployment | [Sign Up](https://azure.microsoft.com/) |

### 2. Required Tools
| Tool | Purpose | Install Command |
|------|---------|-----------------|
| Git | Version control | sudo apt install git |
| Python 3.10+ | Runtime | sudo apt install python3.10 |
| pip | Python package manager | sudo apt install python3-pip |
| Docker | Containerization | [Install Docker](https://docs.docker.com/engine/install/) |
| Azure CLI | Azure management | curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash |

---

## Option 1: Cloud Deployment (Recommended)

Deploy STRIDE + Momento on Azure Kubernetes Service (AKS) or Azure Container Instances (ACI) for scalability and reliability.

---

### Step 1: Set Up Azure Resources

#### 1.1 Install Azure CLI
For Debian/Ubuntu:
curl -sL https://aka.ms/InstallAzureCLIDeb | sudo bash
az --version

#### 1.2 Log in to Azure
az login

#### 1.3 Create a Resource Group
az group create --name stride-resources --location eastus

#### 1.4 Create a Container Registry (ACR)
az acr create --resource-group stride-resources --name strideAcr --sku Basic
