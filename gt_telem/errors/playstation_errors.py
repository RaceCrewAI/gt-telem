class PlayStationNotFoundError(Exception):
    def __init__(self, message="Playstation not found on this network."):
        super().__init__(message)


class PlayStationOnStandbyError(Exception):
    def __init__(self, playstation_ip):
        message = f"Playstation {'at '+playstation_ip+' ' if playstation_ip else ''}is on standby."
        super().__init__(message)
