+++
title = 'tshark & Wireshark'
categories = ['Forensics']
date = "2026-08-23T14:45:00+01:00"
scrollToTop = true
+++

# tshark & Wireshark: Reading Packet Captures

When a forensics challenge hands you a `.pcap` or `.pcapng`, [Wireshark](https://www.wireshark.org/) and its command-line sibling **tshark** are how you turn a wall of packets into an answer. Wireshark's GUI is unbeatable for exploring an unfamiliar capture; `tshark` is unbeatable for extracting exactly the fields you need into a form you can script against. You'll use both — GUI to find the needle, `tshark` to pull it out in bulk.

This guide is built around *Rubik's Cube* from Brunner 2026, a capture of **Bluetooth Low Energy (BLE)** traffic from a smart Rubik's cube that had to be decoded move-by-move.

## Installation

```bash
# Debian/Ubuntu
sudo apt install wireshark tshark
# macOS
brew install --cask wireshark   # includes tshark
```

Allowing non-root capture is offered during install; for reading existing pcaps you don't need it.

## First look

Open the capture and get your bearings:

```bash
wireshark capture.pcapng          # GUI
tshark -r capture.pcapng | head   # dump packets to the terminal
```

Before anything else, ask Wireshark what's *in* the capture — the **Protocol Hierarchy** (`Statistics → Protocol Hierarchy`, or the `tshark` equivalent) tells you at a glance whether you're looking at HTTP, DNS, USB, or — as in *Rubik's Cube* — a stack of Bluetooth HCI / ATT frames:

```bash
tshark -r capture.pcapng -q -z io,phs
```

## Display filters: finding the needle

Wireshark's display-filter syntax is the core skill. Type it into the GUI filter bar, or pass it to `tshark` with `-Y`:

```bash
tshark -r capture.pcapng -Y 'http.request'          # only HTTP requests
tshark -r capture.pcapng -Y 'dns.qry.name'          # DNS queries
tshark -r capture.pcapng -Y 'tcp.port == 1337'
tshark -r capture.pcapng -Y 'frame contains "flag"' # byte-string search
```

Filters compose with `&&`, `||`, `!`, and comparison operators — `ip.addr == 10.0.0.5 && tcp.flags.syn == 1`.

## Extracting fields with -T fields

This is where `tshark` earns its place. Instead of eyeballing packets, print chosen fields as columns you can pipe into Python:

```bash
tshark -r capture.pcapng -Y 'btatt.opcode' \
       -T fields -e frame.number -e btatt.handle -e btatt.value
```

- `-T fields` switches to field-extraction mode.
- `-e <field>` names each field to print (repeatable). Field names are the same tokens as display filters — click any field in the GUI and its name shows in the status bar.
- Add `-E separator=,` `-E header=y` to produce clean CSV.

For *Rubik's Cube*, the winning move was pulling every ATT write value and its handle:

```bash
tshark -r capture.pcapng -Y 'btatt.opcode == 0x12' \
       -T fields -e btatt.value > cube_frames.txt
```

…then decoding those payloads in Python.

## Bluetooth / BLE specifics

BLE captures use a family of protocols worth knowing:

- **`btatt`** — the Attribute Protocol: the actual reads/writes/notifications. This is where device data lives.
- **`btatt.opcode`** — the operation (e.g. `0x12` Write Request, `0x1b` Handle Value Notification).
- **`btatt.handle`** / **`btatt.value`** — which attribute, and its bytes.
- **`btgatt`**, **`bthci_*`** — GATT services and the lower HCI layer.

The general BLE forensics recipe: filter to `btatt`, identify which handle carries the interesting stream, extract its `btatt.value` payloads with `-T fields`, then reconstruct the application-layer meaning. In the cube's case those payloads were AES-128-ECB encrypted with a fixed, publicly documented device key — decrypt, validate the CRC16/MODBUS checksum, and each frame became a cube move. (I keep detailed notes on the QiYi smart-cube packet format for exactly this kind of challenge.)

## Other everyday tricks

- **Follow a stream** — GUI: right-click → `Follow → TCP/UDP/HTTP Stream` to reassemble a conversation into readable text.
- **Export objects** — `File → Export Objects → HTTP` (or SMB/FTP-DATA) carves transferred files straight out of the capture. CLI: `tshark -r cap.pcap --export-objects http,./out/`.
- **Decode As** — force Wireshark to interpret a port as a given protocol when it guesses wrong.
- **Statistics → Conversations / Endpoints** — who talked to whom, and how much.

## Best practices

- **Protocol Hierarchy first.** Know what's in the capture before you filter — it stops you hunting for HTTP in a USB capture.
- **Explore in the GUI, extract with tshark.** Find the field by clicking in Wireshark, copy its name, then script the bulk pull with `-T fields`.
- **Let the payload out cleanly.** For binary application data, extract raw `-e ...value` bytes and do the decoding in Python — don't fight Wireshark's display formatting.
- **Search broadly, then narrow.** `frame contains "flag"` or a `-Y 'frame matches "..."'` regex often shortcuts the whole analysis.

## Conclusion

Most pcap challenges are really "find the one conversation that matters, then decode its payload." Wireshark's filters and stream-following get you to that conversation; `tshark -T fields` gets the payload out in a form you can compute on. Between the two, a capture stops being a wall of hex and becomes a transcript. Happy sniffing!
