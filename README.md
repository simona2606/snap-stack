# Snap Stack - OpenStack Plugin

Snap Stack è un plugin avanzato per OpenStack che automatizza la gestione degli snapshot e il ripristino dei volumi. Offre una soluzione scalabile e configurabile per migliorare la resilienza dei volumi e ottimizzare l'uso dello storage.

## Prerequisiti

Per utilizzare Snap Stack, è necessario avere **DevStack** installato. Le istruzioni ufficiali per installarlo correttamente sono le seguenti:

- [Guida all'installazione di DevStack](https://docs.openstack.org/devstack/latest/)

## Funzionalità Principali

- **Automazione degli snapshot**: Creazione pianificata di snapshot a intervalli definiti.
- **Monitoraggio continuo**: Controllo dello stato dei volumi con rilevazione di anomalie.
- **Ripristino automatico**: Recupero rapido dei volumi utilizzando l'ultimo snapshot valido.
- **Ottimizzazione dello storage**: Gestione degli snapshot obsoleti per un uso efficiente delle risorse.
- **Notifiche in tempo reale**: Email per avvisare gli amministratori di eventuali errori o attività importanti.

## Istruzioni per l'Installazione

### 1. Configurare `local.conf`

Per abilitare Snap Stack bisogna aggiungere il seguente snippet al file `local.conf` dell'installazione di DevStack:

```bash
[[local|localrc]]
   ...
enable_plugin snap-stack https://github.com/tuo-username/snap-stack.git main
```

### 2. Avviare lo script di installazione

Eseguire lo script stack.sh per configurare l'ambiente DevStack e includere Snap Stack:
```bash
./stack.sh
```

Una volta completato, Snap Stack sarà pronto per essere utilizzato.

### 3. Accedere all'interfaccia

Dopo l'installazione, è possibile accedere a Snap Stack visitando:
```bash
http://<devstack_host>:5235
```
Da qui si possono gestire i volumi, pianificare snapshot e configurare il sistema.
