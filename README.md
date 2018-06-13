The pyabpx.py script provides the ability to perform audio hardware [ABX tests](https://en.wikipedia.org/wiki/ABX_test)
using an FT245RL based USB relay like [this one](https://smile.amazon.com/gp/product/B074MPWFF3/ref=oh_aui_search_detailpage?ie=UTF8&psc=1).
It is designed to treat two male 3.5mm TRS connectors as inputs A and B (e.g.
connecting to two different amps), and output to a 3.5mm female TRS
jack (e.g. headphones).

![ABX Tester]

## Hardware Build Instructions
### Required Parts

Total cost about $50, but with plenty of left over connectors and wire.

- 1 x [USB Relay](https://smile.amazon.com/gp/product/B074MPWFF3/ref=oh_aui_search_detailpage?ie=UTF8&psc=1)
- 2 x [3.5mm TRS Male Terminal Connectors](https://smile.amazon.com/gp/product/B016W9P4N0)
- 2 x [3.5mm TRS Female Terminal Block Panel](https://smile.amazon.com/gp/product/B077XPSKQD)
- [Hook Up Wire](https://smile.amazon.com/gp/product/B01LH1G2IE)

### Wiring

- Wire right channel of A cable to off (normally closed) terminal of relay 1
- Wire right channel of B cable to on (normally open) terminal of relay 1
- Wire left channel of A cable to off (normally closed) terminal of relay 2
- Wire left channel of B cable to on (normally open) terminal of relay 2
- Wire right channel of female output cable to common terminal of relay 1
- Wire left channel of female output cable to common terminal of relay 1
- Wire ground of A cable to off (normally closed) terminal of relay 3
- Wire ground of B cable to on (normally open) terminal of relay 3

## Command Line

Example: `sudo python pyabx.py A90799W0 10 "MacBook Air" "Magni 3"`

Arguments:

1. USB relay id (you can get a list of connected relays by running the script without arguments)
2. Number of trials (you'll need at least 10 to get a statistically significant result)
3. Name of source A
4. Name of source B

## Testing Tips

1. The script is programmed so that you'll always hear switching when switching to/from x (unknown)
2. The USB relay has LEDs indicating which relays are on. Keep it out of sight while testing to avoid biasing yourself
3. Run the program once so that you can switch between A and B to volume match both (ideally using a measurement tool like a [MiniDSP E.A.R.S](https://www.minidsp.com/products/acoustic-measurement/ears-headphone-jig))
