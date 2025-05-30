// Copyright (c) 2011-2020 The Andaluzcoin Core developers
// Distributed under the MIT software license, see the accompanying
// file COPYING or http://www.opensource.org/licenses/mit-license.php.

#ifndef ANDALUZCOIN_MAPPORT_H
#define ANDALUZCOIN_MAPPORT_H

static constexpr bool DEFAULT_NATPMP = false;

enum MapPortProtoFlag : unsigned int {
    NONE = 0x00,
    // 0x01 was for UPnP, for which we dropped support.
    PCP = 0x02,   // PCP with NAT-PMP fallback.
};

void StartMapPort(bool use_pcp);
void InterruptMapPort();
void StopMapPort();

#endif // ANDALUZCOIN_MAPPORT_H
