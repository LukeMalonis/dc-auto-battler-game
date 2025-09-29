# combat.py
import pygame
import random


class CombatManager:
    def __init__(self):
        self.combat_active = False

    def start_combat(self, player_board, opponent_board):
        """Start combat between player and opponent boards"""
        self.combat_active = True

        # Calculate total stats for each team
        player_health = sum(unit.health for row in player_board for unit in row if unit and unit.health > 0)
        player_damage = sum(unit.damage for row in player_board for unit in row if unit and unit.health > 0)

        opponent_health = sum(unit.health for row in opponent_board for unit in row if unit and unit.health > 0)
        opponent_damage = sum(unit.damage for row in opponent_board for unit in row if unit and unit.health > 0)

        print(
            f"Combat: Player {player_health}HP/{player_damage}DMG vs Opponent {opponent_health}HP/{opponent_damage}DMG")

        # Determine winner based on combined health + damage
        player_power = player_health + player_damage
        opponent_power = opponent_health + opponent_damage

        if player_power > opponent_power:
            print("Player wins combat!")
            return True  # Player wins
        else:
            print("Opponent wins combat!")
            return False  # Opponent wins

    def strengthen_opponent(self, opponent_board, round_number):
        """Make opponent board stronger each round"""
        for y, row in enumerate(opponent_board):
            for x, unit in enumerate(row):
                if unit:
                    # Increase stats based on round
                    stat_increase = round_number * 0.1  # 10% increase per round
                    unit.health = int(unit.health * (1 + stat_increase))
                    unit.damage = int(unit.damage * (1 + stat_increase))
                    unit.max_health = unit.health