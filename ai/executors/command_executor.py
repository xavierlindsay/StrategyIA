# Under MIT License, see LICENSE.txt

from ai.executors.executor import Executor
from RULEngine.Command import command
from RULEngine.Util.Pose import Pose
from RULEngine.Util.constant import PLAYER_PER_TEAM
from ai.Util.ai_command import AICommand, AICommandType


class CommandExecutor(Executor):
    def __init__(self, p_world_state):
        super().__init__(p_world_state)

    def exec(self):

        self._clear_last_packet_commands()
        self._generate_command()
        self._clear_ai_commands()
        return

    def _clear_last_packet_commands(self):
        self.ws.play_state.ready_to_ship_robot_packet_list.clear()

    def _clear_ai_commands(self):
        self.ws.play_state.current_ai_commands.clear()

    def _generate_command(self):
        ai_command_dict = self._retrieve_commands()

        # TODO: remplacer la constante PLAYER_PER_TEAM par les clefs d'un dictionnaire contenant les robots dans le game_state
        for player_id, ai_command in ai_command_dict.items():
            self.ws.play_state.ready_to_ship_robot_packet_list.append(self._parse_ai_command(ai_command,
                                                                      player_id))
        return self.ws.play_state.ready_to_ship_robot_packet_list

    def _retrieve_commands(self):
        return self.ws.play_state.current_ai_commands

    def _parse_ai_command(self, ai_command, player_id):
        if ai_command is not None:
            if ai_command.command == AICommandType.KICK:
                return self._generate_kick_command(ai_command.kick_strength, player_id)

            elif ai_command.command == AICommandType.MOVE:
                assert (isinstance(ai_command.pose_goal, Pose))
                return self._generate_move_command(ai_command.pose_goal, player_id)

        return self._generate_empty_command(player_id)

    def _retrieve_player(self, player_id):
        return self.ws.game_state.my_team.players[player_id]

    def _generate_kick_command(self, p_kick_strength, player_id):
        kick_strength = self._sanitize_kick_strength(p_kick_strength)
        return command.Kick(self._retrieve_player(player_id), kick_strength)

    def _generate_move_command(self, p_move_destination, player_id):
        return command.MoveToAndRotate(self._retrieve_player(player_id), p_move_destination)

    def _generate_empty_command(self, player_id):
        # Envoi d'une command vide qui fait l'arrêt du robot
        return command.Stop(self._retrieve_player(player_id))

    @staticmethod
    def _sanitize_kick_strength(p_kick_strength):
        if p_kick_strength > 1:
            print("Warning: kick strength devrait être contenu dans l'intervale [0, 1].")
            return 1
        else:
            return p_kick_strength
