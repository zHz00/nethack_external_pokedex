# Running NetHack External Pokedex over network

It's possible to set up an SSH server specifically to run NetHack External Pokedex. This project has not been audited for security and it's recommended to use sandboxing and the least possible privileges to minimize risks.

`Containerfile` describes an example container image that includes NetHack External Pokedex and the Dropbear SSH server.
It's recommended to use [Podman](https://podman.io/) insted of Docker because it's easier to run it as an unprivileged user on the host system.

To build the container image, go to the project root and run:

```sh
podman build -t pokedex -f deploy/Containerfile .
```

Once built, the container can be started as follows:

```sh
podman run -p 3722:22 pokedex
```

The application can be accessed via SSH as the user `pokedex` to 0.0.0.0:3722. There is no password by default.

```sh
ssh -p 3722 pokedex@0.0.0.0
```

## Using Docker

If you prefer, you can replace `podman` with `docker` the above commands and it should work fine. Beware that the Docker daemon runs as root by default.

## Listening on a privileged port (Linux-specific)

If you'd like to start your SSH server on a low-number port (<1024 by default) it's recommended that you create a firewall rule to redirect traffic from the desired port to the one that Podman binds to. Alternatively, run Podman or Docker as root, or add the `NET_BIND_SERVICE` capability.

Below is an example `nftables` rule. Note that podman still needs to be listening on the same IP address that you would use for accepting inbound traffic normally (usually not localhost).

```nftables
iif eth0 tcp dport 22 redirect to :3722
```

Make sure your port 22 is not used for anything else (like the actual administrative SSH server).
