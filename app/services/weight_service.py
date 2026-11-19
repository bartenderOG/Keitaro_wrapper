def calculate_weights(
    offers: list[dict],
) -> list[dict]:
    active_offers = [
        offer
        for offer in offers
        if offer["status"] == "active"
    ]

    if not active_offers:
        return []

    pinned_offers = [
        offer
        for offer in active_offers
        if offer["is_pinned"]
    ]

    unpinned_offers = [
        offer
        for offer in active_offers
        if not offer["is_pinned"]
    ]

    pinned_weight = sum(
        offer["weight"]
        for offer in pinned_offers
    )

    remaining_weight = 100 - pinned_weight

    if remaining_weight < 0:
        raise ValueError("Pinned weights cannot exceed 100%")

    if unpinned_offers:
        base_weight = remaining_weight // len(unpinned_offers)
        remainder = remaining_weight % len(unpinned_offers)

        for index, offer in enumerate(unpinned_offers):
            offer["weight"] = base_weight

            if index < remainder:
                offer["weight"] += 1

    return active_offers
