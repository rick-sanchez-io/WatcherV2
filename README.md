# WatcherV2
Smart x-ui traffic watcher with safe startup bootstrap

![banner](assets/Screenshot_2026-05-13-20-45-26-489_com.android.chrome~2.jpg)

# Important Warning

**The only official version of watcherV2 is available through this GitHub page.
Do not use other versions shared in different telegram channels or hosted on other GitHub pages, as the risk of scams and theft is extremely high** ⚠️

---

# x-ui Expire Watcher

A smart traffic watcher for x-ui panels (only).

watcherV2 is an open source project that watches your x-ui traffic database directly and restarts xray when a client exceeds their total quota.

---

# Features of the watcherV2

* wont crack under high pressure 
* Safe startup bootstrap
* Colored logs
* restarts xray instead of the x-ui
* Lightweight polling
* Expired Clients removed from main loop
* Automatic recheck system
* Doesn't spam xray restarts

---

# How This Thing Works

The script reads this database:

```bash
/etc/x-ui/x-ui.db
```

It checks:

```text
used traffic > total quota
```

If a client exceeded the quota:

* user gets marked as expired
* xray gets restarted
* expired user will be disconnected.

Simple. Efficient.

---

# Installation

## Screen :


### 1. Clone the repository
```bash
git clone https://github.com/rick-sanchez-io/WatcherV2.git
cd WatcherV2
```

---

### 2. Run installer

```bash
sudo bash scripts/install.sh
```

The installer will:

* copy the watcher script to `/opt/watcherV2/watcher2.py`
* create `watcher2.service` in systemd
* start and enable the service automatically

### 3. Check service status

```bash
systemctl status watcher2.service
```

### 4. View live logs

```bash
journalctl -u watcher2.service -f
```
---

# Why is this script effective?

Based on the tests performed, this script has an error margin of around 1 to 10 MB per user, and in the worst-case scenario, around 20 to 30 MB.
It can easily be used for panels with a large number of users.

![banner](assets/Screenshot_2026-05-13-23-22-53-914_com.server.auditor.ssh.client~2.jpg)
*as you can see in the image , the error rate was 68169 bytes ( 68.169 KB )*
