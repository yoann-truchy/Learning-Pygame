from dataclasses import dataclass, field

@dataclass
class Score:
    left: int
    tight: int

@dataclass
class Screen_config:
    width: int = 1280
    height: int = 720
    max_refresh_rate: int = 60
    
@dataclass
class Mapping_config:
    player1_up_key: str = "z"
    player1_down_key: str = "s"

@dataclass
class Game_config:
    screen: Screen_config =  field(default_factory=Screen_config)
    mapping:Mapping_config = field(default_factory=Mapping_config)

    backgroud_color: tuple = (0, 0, 50)
    player_color: tuple = (200, 200, 200)
    ball_color: tuple = (150, 150, 150)

    debug: bool = False