# SPDX-License-Identifier: LGPL-2.1-or-later

import pytest

import libnmstate
from libnmstate.iplib import is_ipv6_link_local_addr
from libnmstate.schema import Interface
from libnmstate.schema import InterfaceIPv4
from libnmstate.schema import InterfaceIPv6
from libnmstate.schema import InterfaceState
from libnmstate.schema import InterfaceType
from libnmstate.schema import Veth

from .testlib import assertlib
from .testlib import cmdlib
from .testlib import statelib
from .testlib.apply import apply_with_description
from .testlib.dummy import nm_unmanaged_dummy
from .testlib.env import is_el8
from .testlib.ifacelib import get_mac_address
from .testlib.iproutelib import ip_monitor_assert_stable_link_up
from .testlib.iproutelib import iproute_get_ip_addrs_with_order
from .testlib.servicelib import disable_service
from .testlib.yaml import load_yaml

# TEST-NET addresses: https://tools.ietf.org/html/rfc5737#section-3
IPV4_ADDRESS1 = "192.0.2.251"
IPV4_ADDRESS2 = "192.0.2.252"
IPV4_ADDRESS3 = "198.51.100.249"
IPV4_ADDRESS4 = "198.51.100.250"
# IPv6 Address Prefix Reserved for Documentation:
# https://tools.ietf.org/html/rfc3849
IPV6_ADDRESS1 = "2001:db8:1::1"
IPV6_ADDRESS2 = "2001:db8:2::1"
IPV6_LINK_LOCAL_ADDRESS1 = "fe80::1"
IPV6_LINK_LOCAL_ADDRESS2 = "fe80::2"

DUMMY1 = "dummy1"


@pytest.fixture
def setup_dummy1_ipv4():
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        f"Configure the {DUMMY1} dummy device with the address "
        "192.0.2.251/24 and dhcp4 disabled",
        desired_state,
    )
    yield desired_state
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.ABSENT,
            }
        ]
    }
    apply_with_description(f"Remove {DUMMY1} device", desired_state)


@pytest.fixture
def setup_dummy1_ipv6():
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        f"Configure the {DUMMY1} dummy device with the address "
        "2001:db8:1::1/64, dhcp6 disabled, autoconf disabled",
        desired_state,
    )
    yield desired_state
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.ABSENT,
            }
        ]
    }
    apply_with_description(f"Remove {DUMMY1} device", desired_state)


@pytest.fixture
def setup_eth1_static_ip(eth1_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the eth1 ethernet device with the address "
        "192.0.2.251/24, 2001:db8:1::1/64, dhcp4 disabled, dhcp6 disabled, "
        "autoconf disabled",
        desired_state,
    )

    return desired_state


@pytest.fixture
def setup_dummy1_ipv6_disable(eth1_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {InterfaceIPv6.ENABLED: False},
            }
        ]
    }
    apply_with_description(
        "Configure the dummy1 dummy device with IPv6 disabled", desired_state
    )

    return desired_state


def test_add_static_ipv4_with_full_state(eth1_up):
    desired_state = statelib.show_only(("eth1",))
    eth1_desired_state = desired_state[Interface.KEY][0]

    eth1_desired_state[Interface.STATE] = InterfaceState.UP
    eth1_desired_state[Interface.IPV4][InterfaceIPv4.ENABLED] = True
    eth1_desired_state[Interface.IPV4][InterfaceIPv4.ADDRESS] = [
        {
            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS3,
            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
        }
    ]
    apply_with_description(
        "Configure the eth1 ethernet device with the address "
        "198.51.100.249/24 and dhcp4 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_add_static_ipv4_with_min_state(eth2_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS4,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the eth2 ethernet device with address 198.51.100.250/24 "
        "and dhcp4 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_remove_static_ipv4(setup_dummy1_ipv4):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.IPV4: {InterfaceIPv4.ENABLED: False},
            }
        ]
    }

    apply_with_description(
        f"Configure the {DUMMY1} dummy device with IPv4 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_edit_static_ipv4_address_and_prefix(setup_dummy1_ipv4):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS2,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 30,
                        }
                    ],
                },
            }
        ]
    }

    apply_with_description(
        f"Configure the {DUMMY1} dummy device with address 192.0.2.252/30",
        desired_state,
    )

    assertlib.assert_state(desired_state)


def test_add_ifaces_with_same_static_ipv4_address_in_one_transaction(
    eth1_up, eth2_up
):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
            },
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
            },
        ]
    }

    apply_with_description(
        "Configure the eth1 ethernet device with address "
        "192.0.2.251/24 and dhcp4 disabled, configure the eth2 ethernet "
        "device with address 192.0.2.251/24 and dhcp4 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


def test_add_iface_with_same_static_ipv4_address_to_existing(
    setup_dummy1_ipv4, eth2_up
):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the eth2 ethernet device with address 192.0.2.251/24 and "
        "dhcp4 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_add_static_ipv6_with_full_state(eth1_up):
    desired_state = statelib.show_only(("eth1",))
    eth1_desired_state = desired_state[Interface.KEY][0]
    eth1_desired_state[Interface.STATE] = InterfaceState.UP
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ENABLED] = True
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS] = [
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS2,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
        # This sequence is intentionally made for IP address sorting.
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
    ]
    apply_with_description(
        "Configure the eth1 ethernet device with the address "
        "2001:db8:2::1/64 and 2001:db8:1::1/64, dhcp6 disabled and autoconf "
        "disabled",
        desired_state,
    )
    assertlib.assert_state(desired_state)


def test_add_static_ipv6_with_link_local(eth1_up):
    desired_state = statelib.show_only(("eth1",))
    eth1_desired_state = desired_state[Interface.KEY][0]
    eth1_desired_state[Interface.STATE] = InterfaceState.UP
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ENABLED] = True
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS] = [
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_LINK_LOCAL_ADDRESS1,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
    ]

    apply_with_description(
        "Configure the eth1 ethernet device with address 2001:db8:1::1/64, "
        "dhcp6 disabled, and autoconf disabled",
        desired_state,
    )

    # Make sure only the link local address got ignored.
    cur_state = statelib.show_only(("eth1",))
    eth1_cur_state = cur_state[Interface.KEY][0]
    assert (
        eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS][0]
        not in eth1_cur_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )
    assert (
        eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS][1]
        in eth1_cur_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )


def test_add_static_ipv6_with_link_local_only(eth1_up):
    desired_state = statelib.show_only(("eth1",))
    eth1_desired_state = desired_state[Interface.KEY][0]
    eth1_desired_state[Interface.STATE] = InterfaceState.UP
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ENABLED] = True
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS] = [
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_LINK_LOCAL_ADDRESS1,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
        {
            InterfaceIPv6.ADDRESS_IP: IPV6_LINK_LOCAL_ADDRESS2,
            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
        },
    ]

    apply_with_description(
        "Configure the eth1 ethernet device with IPv6 link local address "
        "only",
        desired_state,
    )

    # Make sure the link local address got ignored.
    cur_state = statelib.show_only(("eth1",))
    eth1_cur_state = cur_state[Interface.KEY][0]
    assert (
        eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS][0]
        not in eth1_cur_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )
    assert (
        eth1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS][1]
        not in eth1_cur_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )


@pytest.mark.tier1
def test_add_static_ipv6_with_no_address(eth1_up):
    desired_state = statelib.show_only(("eth1",))
    eth1_desired_state = desired_state[Interface.KEY][0]
    eth1_desired_state[Interface.STATE] = InterfaceState.UP
    eth1_desired_state[Interface.IPV6][InterfaceIPv6.ENABLED] = True

    apply_with_description(
        "Configure the eth1 ethernet device with IPv6 link local address "
        "only",
        desired_state,
    )

    cur_state = statelib.show_only(("eth1",))
    eth1_cur_state = cur_state[Interface.KEY][0]
    # Should have at least 1 link-local address.
    assert len(eth1_cur_state[Interface.IPV6][InterfaceIPv6.ADDRESS]) >= 1


def test_add_static_ipv6_with_min_state(eth2_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the eth2 ethernet device with the address "
        "2001:db8:1::1/64, dhcp6 disabled and autoconf disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_disable_static_ipv6(setup_dummy1_ipv6):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.IPV6: {InterfaceIPv6.ENABLED: False},
            }
        ]
    }

    apply_with_description(
        f"Configure the {DUMMY1} dummy device with IPv6 disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


@pytest.mark.tier1
def test_disable_static_ipv6_and_rollback(setup_dummy1_ipv6):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.IPV6: {InterfaceIPv6.ENABLED: False},
                "foo": "bad_value",
            }
        ]
    }

    with pytest.raises(
        (
            libnmstate.error.NmstateVerificationError,
            libnmstate.error.NmstateValueError,
        )
    ):
        libnmstate.apply(desired_state)

    assertlib.assert_state(setup_dummy1_ipv6)


@pytest.mark.tier1
def test_enable_ipv6_and_rollback_to_disable_ipv6(setup_dummy1_ipv6_disable):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
                "foo": "bad_value",
            }
        ]
    }

    with pytest.raises(
        (
            libnmstate.error.NmstateVerificationError,
            libnmstate.error.NmstateValueError,
        )
    ):
        libnmstate.apply(desired_state)

    assertlib.assert_state(setup_dummy1_ipv6_disable)


@pytest.mark.tier1
def test_edit_static_ipv6_address_and_prefix(setup_dummy1_ipv6):
    dummy1_setup = setup_dummy1_ipv6[Interface.KEY][0]
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: DUMMY1,
                Interface.TYPE: InterfaceType.DUMMY,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS2,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }

    apply_with_description(
        f"Configure the dummy device {DUMMY1} with the address "
        "2001:db8:2::1/64",
        desired_state,
    )
    dummy1_desired_state = desired_state[Interface.KEY][0]
    current_state = statelib.show_only((DUMMY1,))

    dummy1_current_state = current_state[Interface.KEY][0]

    assert (
        dummy1_desired_state[Interface.IPV6][InterfaceIPv6.ADDRESS][0]
        in dummy1_current_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )

    assert (
        dummy1_setup[Interface.IPV6][InterfaceIPv6.ADDRESS][0]
        not in dummy1_current_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
    )


def test_add_ifaces_with_same_static_ipv6_address_in_one_transaction(
    eth1_up, eth2_up
):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            },
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            },
        ]
    }

    apply_with_description(
        "Configure the ethernet device eth1 with the address "
        "2001:db8:1::1/64, dhcp6 disabled and autoconf disabled, configure "
        "the ethernet device eth2 with the address 2001:db8:1::1/64, dhcp6 "
        "disabled and autoconf disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


def test_add_iface_with_same_static_ipv6_address_to_existing(
    setup_dummy1_ipv6, eth2_up
):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth2",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth2 to have the address "
        "2001:db8:1::1/64, dhcp6 disabled, autoconf disabled",
        desired_state,
    )

    assertlib.assert_state(desired_state)


def test_add_iface_with_static_ipv6_expanded_format(eth1_up):
    ipv6_addr_lead_zeroes = "2001:0db8:85a3:0000:0000:8a2e:0370:7331"
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: eth1_up[Interface.KEY][0][Interface.NAME],
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: ipv6_addr_lead_zeroes,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 with the address "
        "2001:db8:85a3::8a2e:370:7331/64, dhcp6 disabled, autoconf disabled",
        desired_state,
    )
    assertlib.assert_state(desired_state)


@pytest.mark.tier1
@ip_monitor_assert_stable_link_up(DUMMY1)
def test_modify_ipv4_with_reapply(setup_dummy1_ipv4):
    ipv4_addr = IPV4_ADDRESS2
    ipv4_state = setup_dummy1_ipv4[Interface.KEY][0][Interface.IPV4]
    ipv4_state[InterfaceIPv4.ADDRESS][0][InterfaceIPv4.ADDRESS_IP] = ipv4_addr
    apply_with_description(
        f"Configure the dummy device {DUMMY1} to have the address "
        "192.0.2.252/24",
        setup_dummy1_ipv4,
    )

    assertlib.assert_state(setup_dummy1_ipv4)


@pytest.mark.tier1
@ip_monitor_assert_stable_link_up(DUMMY1)
def test_modify_ipv6_with_reapply(setup_dummy1_ipv6):
    ipv6_addr = IPV6_ADDRESS2
    ipv6_state = setup_dummy1_ipv6[Interface.KEY][0][Interface.IPV6]
    ipv6_state[InterfaceIPv6.ADDRESS][0][InterfaceIPv6.ADDRESS_IP] = ipv6_addr
    apply_with_description(
        f"Configure the dummy device {DUMMY1} to have the address "
        "2001:db8:2::1/64",
        setup_dummy1_ipv6,
    )

    assertlib.assert_state(setup_dummy1_ipv6)


@pytest.mark.tier1
def test_get_ip_address_from_unmanaged_dummy():
    with nm_unmanaged_dummy(DUMMY1):
        cmdlib.exec_cmd(
            f"ip addr add {IPV4_ADDRESS1}/24 dev {DUMMY1}".split(), check=True
        )
        cmdlib.exec_cmd(
            f"ip -6 addr add {IPV6_ADDRESS2}/64 dev {DUMMY1}".split(),
            check=True,
        )
        iface_state = statelib.show_only((DUMMY1,))[Interface.KEY][0]
        # Remove IPv6 link local address
        iface_state[Interface.IPV6][InterfaceIPv6.ADDRESS] = [
            addr
            for addr in iface_state[Interface.IPV6][InterfaceIPv6.ADDRESS]
            if not is_ipv6_link_local_addr(
                addr[InterfaceIPv6.ADDRESS_IP],
                addr[InterfaceIPv6.ADDRESS_PREFIX_LENGTH],
            )
        ]

        assert iface_state[Interface.IPV4] == {
            InterfaceIPv4.ENABLED: True,
            InterfaceIPv4.ADDRESS: [
                {
                    InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                    InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                }
            ],
        }

        assert iface_state[Interface.IPV6] == {
            InterfaceIPv6.ENABLED: True,
            InterfaceIPv6.ADDRESS: [
                {
                    InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS2,
                    InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                }
            ],
        }


def test_ignore_invalid_ip_on_absent_interface(eth1_up):
    libnmstate.apply(
        {
            Interface.KEY: [
                {
                    Interface.NAME: "eth1",
                    Interface.STATE: InterfaceState.ABSENT,
                    Interface.IPV4: {
                        InterfaceIPv4.ENABLED: True,
                        InterfaceIPv4.ADDRESS: [
                            {
                                InterfaceIPv4.ADDRESS_IP: "a.a.a.a",
                                InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                            }
                        ],
                    },
                    Interface.IPV6: {
                        InterfaceIPv6.ENABLED: True,
                        InterfaceIPv6.ADDRESS: [
                            {
                                InterfaceIPv6.ADDRESS_IP: "::g",
                                InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                            }
                        ],
                    },
                }
            ]
        }
    )


@pytest.mark.tier1
def test_preserve_ip_conf_if_not_mentioned(setup_eth1_static_ip):
    desired_state = setup_eth1_static_ip
    libnmstate.apply(
        {
            Interface.KEY: [
                {
                    Interface.NAME: "eth1",
                }
            ]
        }
    )
    assertlib.assert_state_match(desired_state)


def test_static_ip_kernel_mode():
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "test-veth1",
                Interface.TYPE: InterfaceType.VETH,
                Interface.STATE: InterfaceState.UP,
                Veth.CONFIG_SUBTREE: {
                    Veth.PEER: "test-veth1.ep",
                },
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        }
                    ],
                },
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        }
                    ],
                },
            }
        ]
    }
    try:
        apply_with_description(
            "Configure the ethernet interface test-veth1 with the peer "
            "test-veth1.ep, configure the address "
            "192.0.2.251/24 and address 2001:db8:1::1/64",
            desired_state,
            kernel_only=True,
        )
        assertlib.assert_state_match(desired_state)
    finally:
        apply_with_description(
            "Delete the ethernet interface test-veth1",
            {
                Interface.KEY: [
                    {
                        Interface.NAME: "test-veth1",
                        Interface.TYPE: InterfaceType.VETH,
                        Interface.STATE: InterfaceState.ABSENT,
                    }
                ]
            },
            kernel_only=True,
        )


def test_merge_ip_enabled_property_from_current(setup_eth1_static_ip):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.IPV4: {
                    InterfaceIPv4.DHCP: True,
                },
                Interface.IPV6: {
                    InterfaceIPv6.DHCP: True,
                    InterfaceIPv6.AUTOCONF: True,
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 with DHCP4, IPv4 auto dns, IPv4 "
        "auto gateway, IPv4 auto routes, DHCP6, autoconf, IPv6 auto dns, "
        "IPv6 auto gateway, IPv6 auto routes",
        desired_state,
    )
    desired_state[Interface.KEY][0][Interface.IPV4][
        InterfaceIPv4.ENABLED
    ] = True
    desired_state[Interface.KEY][0][Interface.IPV6][
        InterfaceIPv6.ENABLED
    ] = True
    assertlib.assert_state_match(desired_state)


def test_preserve_ipv4_addresses_order(eth1_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS2,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        },
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        },
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 to have the address "
        "192.0.2.252/24, 192.0.2.251/24 and dhcp4 disabled",
        desired_state,
    )
    ip_addrs = iproute_get_ip_addrs_with_order(iface="eth1", is_ipv6=False)
    assert ip_addrs[0] == IPV4_ADDRESS2
    assert ip_addrs[1] == IPV4_ADDRESS1


@pytest.mark.skipif(
    is_el8(),
    reason="RHEL 8 hold different IPv6 address order in rpm between "
    "downstream shipped and copr main branch built",
)
def test_preserve_ipv6_addresses_order(eth1_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS2,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        },
                        {
                            InterfaceIPv6.ADDRESS_IP: IPV6_ADDRESS1,
                            InterfaceIPv6.ADDRESS_PREFIX_LENGTH: 64,
                        },
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 with the address "
        "2001:db8:2::1/64, 2001:db8:1::1/64, dhcp6 disabled, autoconf "
        "disabled",
        desired_state,
    )
    ip_addrs = iproute_get_ip_addrs_with_order(iface="eth1", is_ipv6=True)
    assert ip_addrs[0] == IPV6_ADDRESS2
    assert ip_addrs[1] == IPV6_ADDRESS1


def test_remove_all_ip_address(setup_eth1_static_ip):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.ADDRESS: [],
                },
                Interface.IPV6: {
                    InterfaceIPv6.ENABLED: True,
                    InterfaceIPv6.ADDRESS: [],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 with empty address",
        desired_state,
    )
    desired_state[Interface.KEY][0][Interface.IPV4][
        InterfaceIPv4.ENABLED
    ] = False

    assertlib.assert_state_match(desired_state)


def test_ignore_dhcp_client_id_if_static(eth1_up):
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "eth1",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.DHCP: False,
                    InterfaceIPv4.DHCP_CLIENT_ID: "ll",
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        },
                    ],
                },
            }
        ]
    }
    apply_with_description(
        "Configure the ethernet device eth1 with address 192.0.2.251/24 "
        "with dhcp4 disabled",
        desired_state,
    )


def test_mac_address_based_matching(eth1_up):
    eth1_mac = get_mac_address("eth1")
    desired_state = {
        Interface.KEY: [
            {
                Interface.NAME: "test0",
                Interface.TYPE: InterfaceType.ETHERNET,
                Interface.STATE: InterfaceState.UP,
                Interface.IDENTIFIER: Interface.IDENTIFIER_MAC,
                Interface.MAC: eth1_mac,
                Interface.IPV4: {
                    InterfaceIPv4.ENABLED: True,
                    InterfaceIPv4.DHCP: False,
                    InterfaceIPv4.ADDRESS: [
                        {
                            InterfaceIPv4.ADDRESS_IP: IPV4_ADDRESS1,
                            InterfaceIPv4.ADDRESS_PREFIX_LENGTH: 24,
                        },
                    ],
                },
            }
        ]
    }
    apply_with_description(
        f"Set interface holding MAC address {eth1_mac} with "
        "192.0.2.251/24 and profile name test0",
        desired_state,
    )
    expected_state = desired_state
    expected_state[Interface.KEY][0][Interface.NAME] = "eth1"
    expected_state[Interface.KEY][0][Interface.PROFILE_NAME] = "test0"

    assertlib.assert_state(expected_state)


@pytest.fixture
def cleanup_veth1_kernel_mode():
    with disable_service("NetworkManager"):
        yield
        desired_state = load_yaml(
            """---
            interfaces:
            - name: veth1
              type: veth
              state: absent
            """
        )
        apply_with_description(
            "Delete the veth device veth1", desired_state, kernel_only=True
        )


# TODO(Gris): kernel mode cannot remove IP address yet
def test_kernel_mode_static_ip(cleanup_veth1_kernel_mode):
    desired_state = load_yaml(
        """---
        interfaces:
        - name: veth1
          type: veth
          state: up
          veth:
            peer: veth1_peer
          ipv4:
            address:
            - ip: 192.0.2.251
              prefix-length: 24
            dhcp: false
            enabled: true
          ipv6:
            enabled: true
            autoconf: false
            dhcp: false
            address:
              - ip: 2001:db8:1::1
                prefix-length: 64
        """
    )
    apply_with_description(
        "Configure the veth device veth1 with the peer veth1_peer and "
        "address 192.0.2.251/24 and 2001:db8:1::1/64",
        desired_state,
        kernel_only=True,
    )
    assertlib.assert_state_match(desired_state, kernel_only=True)
