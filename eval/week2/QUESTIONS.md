# Week 2 question set and answer key

Ask each question in `/docs` with the matching image from `images/`.
Use the **expected answer** to grade: `correct`, `partial`, `wrong` or `hallucination`.
The type goes in the `question_type` column of the grading sheet.

| # | Image | Type | Question | Expected answer |
|---|---|---|---|---|
| 1 | 01_motherboard_a.jpg | describe | What is in this image? | Inside of an open desktop PC (Dell): motherboard, CPU air shroud, power supply, SATA and ribbon cables, PCIe slots |
| 2 | 01_motherboard_a.jpg | ocr | What brand is shown on the black CPU shroud? | DELL |
| 3 | 01_motherboard_a.jpg | trick | Which graphics card is installed in the PCIe slot? | None visible; the expansion slots are empty |
| 4 | 03_modem_pcb.jpg | describe | What kind of device is this board from? | A modem board (9.6k modem): DB-25 serial connector, phone jacks, transformer, row of indicator LEDs |
| 5 | 03_modem_pcb.jpg | ocr | What is written on the large square chip in the middle? | RC9623DP, R6642-22, ©ROCKWELL 91, MEXICO |
| 6 | 03_modem_pcb.jpg | ocr | What does the round black sticker say? | QC PASSED |
| 7 | 03_modem_pcb.jpg | count | How many red LEDs are on the right edge of the board? | 8 |
| 8 | 03_modem_pcb.jpg | trick | Which of the LEDs are lit? | None; the board is not powered |
| 9 | 04_pedal_pcb_closeup.jpg | describe | What components are in this close-up? | Through-hole resistors (colour bands), a yellow film capacitor marked 473K, electrolytic capacitors |
| 10 | 04_pedal_pcb_closeup.jpg | ocr | What is printed on the yellow capacitor? | 473K (47 nF) |
| 11 | 05_chip_marking.jpg | ocr | What is the part number on this chip? | P8259A (Intel 8259A interrupt controller) |
| 12 | 05_chip_marking.jpg | count | How many pins does this chip have in total? | 28 (DIP-28, 14 per side) |
| 13 | 06_atx_connector.jpg | count | How many pins does this connector have? | 24 (2 rows × 12): ATX 24-pin power |
| 14 | 06_atx_connector.jpg | problem | Is the power cable properly seated in this connector? | No cable is plugged in; the connector is empty |
| 15 | 07_scope_waveforms.jpg | describe | What signals are shown on this oscilloscope? | Two channels: a triangle wave (top) and a square wave (bottom), same frequency |
| 16 | 07_scope_waveforms.jpg | count | How many full periods of the square wave are visible? | About 4 |
| 17 | 08_scope_screen.jpg | ocr | What is the Vpp measurement? | 528.00 mV |
| 18 | 08_scope_screen.jpg | ocr | What is the fall time (tf) and the timebase? | tf = 5.38 µs, timebase 2 µs/div |
| 19 | 08_scope_screen.jpg | ocr | What brand and model is this oscilloscope? | Rohde & Schwarz / Hameg HMO3004 Series |
| 20 | 09_solder_tombstone.jpg | problem | Is there a soldering defect? Which component? | Yes: R107 is "tombstoned" (standing on one end, lifted off a pad). R105 is also shifted off its lower pad |
| 21 | 09_solder_tombstone.jpg | trick | Why is R106 burnt? | It isn't; R106 looks normal |
| 22 | 10_selftest_log.png | problem | Did the test pass? What failed? | Overall FAIL: LAN2 link failed (no carrier); USB3 port 2 warning (480 Mbps instead of 5 Gbps) |
| 23 | 10_selftest_log.png | ocr | What is the board serial number? | TST2611050427 |
| 24 | 10_selftest_log.png | trick | Why did the memory test fail? | It didn't; memory passed with 0 errors |
| 25 | 11_test_report.png | problem | Which test is out of spec, and by how much? | 5V rail: 4.61 V, below the 4.75 V minimum by 0.14 V |
| 26 | 11_test_report.png | count | How many tests passed? | 5 of 6 |
| 27 | 12_modem_pcb_dark_blurry.jpg | describe | What is in this image? | A circuit board (same modem board), rotated, dark and blurry |
| 28 | 12_modem_pcb_dark_blurry.jpg | ocr | What does the round black sticker say? | QC PASSED (hard to read). "Can't read it" is an acceptable `partial` |

**Type totals (28 questions):** describe 5, ocr 10, count 5, problem 4, trick 4.

Tip: ask in a fresh order rather than all questions for one image in a row, and
note the first request after 5+ minutes idle (model load), which is always slow.
