import math
import sys

from kaggle_environments.helpers import Configuration, Observation

from lux import annotate
from lux.constants import Constants
from lux.game import Game
from lux.game_constants import GAME_CONSTANTS
from lux.game_map import RESOURCE_TYPES, Cell
from lux.game_objects import Player

DIRECTIONS = Constants.DIRECTIONS
game_state = None


def agent(observation: Observation, configuration: Configuration):
    global game_state

    ### Do not edit ###
    if observation["step"] == 0:
        game_state = Game()
        game_state._initialize(observation["updates"])
        game_state._update(observation["updates"][2:])
        game_state.id = observation.player
    else:
        game_state._update(observation["updates"])

    actions = []

    ### AI Code goes down here! ###
    player: Player = game_state.players[observation.player]
    opponent: Player = game_state.players[(observation.player + 1) % 2]
    width, height = game_state.map.width, game_state.map.height

    coal_targets: list[Cell] = []
    for y in range(height):
        for x in range(width):
            cell = game_state.map.get_cell(x, y)
            if (
                cell.has_resource()
                and cell.resource.type == Constants.RESOURCE_TYPES.COAL
            ):
                coal_targets.append(cell)

    # we iterate over all our units and do something with them
    for unit in player.units:
        if unit.is_worker() and unit.can_act():
            closest_dist = math.inf
            closest_resource_tile = None
            if unit.get_cargo_space_left() > 0:
                # If the unit is a worker and we have space in cargo, lets find the nearest
                # resource tile and try to mine it
                for resource_tile in coal_targets:
                    if (
                        resource_tile.resource.type == Constants.RESOURCE_TYPES.COAL
                        and not player.researched_coal()
                    ):
                        continue
                    if (
                        resource_tile.resource.type == Constants.RESOURCE_TYPES.URANIUM
                        and not player.researched_uranium()
                    ):
                        continue
                    dist = resource_tile.pos.distance_to(unit.pos)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_resource_tile = resource_tile
                if closest_resource_tile is not None:
                    actions.append(
                        unit.move(unit.pos.direction_to(closest_resource_tile.pos))
                    )
            else:
                # If unit is a worker and there is no cargo space left, and we have cities,
                # lets return to them
                if len(player.cities) > 0:
                    closest_dist = math.inf
                    closest_city_tile = None
                    for k, city in player.cities.items():
                        for city_tile in city.citytiles:
                            dist = city_tile.pos.distance_to(unit.pos)
                            if dist < closest_dist:
                                closest_dist = dist
                                closest_city_tile = city_tile
                    if closest_city_tile is not None:
                        move_dir = unit.pos.direction_to(closest_city_tile.pos)
                        actions.append(unit.move(move_dir))

    # you can add debug annotations using the functions in the annotate object
    # actions.append(annotate.circle(0, 0))

    return actions
