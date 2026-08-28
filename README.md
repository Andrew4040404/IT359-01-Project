# Wireless RSSI Direction Finding and Signals Analysis

## Objectives

1. Receive and decode a router beacon packet out of the air without a modem using HackRF.
2. Calculate RSSI data.
3. Plot location relative to users.

## Success Criteria

1. MAC packet decodes.
2. RSSI data is calculated.
3. The program can analyze and compare packets.
4. Location is accurate.

## Stakeholders

| Role | Name |
| --- | --- |
| Sponsor | Dr. Dean Sanders |
| Project Lead | Max Johnson |
| Deliverables | Andrew Babb |
| Design | Vadim Korypaev |

## Scope Management

### In-Scope Items

- 2.4 GHz Wi-Fi packets.

### Out-of-Scope Items

- All bands outside 2.4 GHz, including 5 GHz.
- All digital and analog signal types not included in 802.11.

### Assumptions and Constraints

- A 2.4 GHz signal is present.

## Timeline

- **August 31 - September 4:** All parts arrive. The unit is assembled and receives data on all antennas.
- **Midterms:** Functional unit; data should be decodable.
- **Finals:** Deliverables are completed, security risks of wireless systems are exemplified, and the software is able to direction-find wireless networks.

## Risk Management

This project revolves around the analysis of router beacon frames between the data link layer and the physical layer of the hybrid OSI/TCP-IP model. Normally, this data is discarded by the modem before reaching the user. This data will be used for pseudo-Doppler direction finding.

The hardware uses four antennas operating in pseudo-Doppler mode to take samples, with a dwell time of 100,000 samples per antenna. The high number of samples per antenna minimizes interference from switching and provides plenty of overhead for decoding frames of 100 to 400 bytes.

Comparing RSSI readings from each antenna allows a user to pinpoint a wireless signal based on the relative signal strength observed at each antenna and the differences between them.

## Resources

### Budget

| Item | Estimated Cost |
| --- | ---: |
| HackRF One (ideally a Pro) | $400 |
| Opera Cake | $190 |
| Four Moxon antennas | $40 |
| **Total** | **$630** |

### Required Tools

- Computer
- HackRF
- Four antennas

### Dependencies

Radioconda and all subsequent dependencies, including the 802.11 module, which is outside the scope of the Radioconda documentation.

## Communication

- **Frequency:** Twice per week during scheduled class time.
- **Channels:** Snapchat and email.

## Action Items

1. Order parts and confirm electronics. *(In progress)*
2. Diagram physical hardware.
3. Write the DSP program in Python/GNU Radio. *(In progress)*
4. Diagram the DSP in GNU Radio. *(Occurs as the program is written)*
5. Write a program to compare beacon packet information.
6. Write a simple program to display location, most likely using Visual Basic because it works well with Python.
7. Write up.