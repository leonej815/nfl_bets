import sqlite3

class Data_Storage:
    # connects to sqlite and creates table to store data if it doesn't exist
    def __init__(self):
        self.conn = sqlite3.connect('./sqlite/nfl_bets.sqlite')
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS nfl_game_data(id INTEGER PRIMARY KEY AUTOINCREMENT,
        year INTEGER, week INTEGER, away TEXT, home TEXT, away_spread REAL, home_spread REAL, total_line REAL, away_score INTEGER, home_score INTEGER,
        
        away_home_game_count INTEGER, away_away_game_count INTEGER, 
        
        away_ppg REAL, away_pass_comp_pg REAL, away_pass_yd_pg REAL, away_pass_td_pg REAL, away_int_thrown_pg REAL, away_sacks_taken_pg REAL, away_rush_att_pg REAL, away_rush_yds_pg REAL, away_rush_td_pg REAL, away_fgm_pg REAL, away_fga_pg REAL, away_pnt_pg REAL, away_3d_conv_pg REAL, away_3d_att_pg REAL, away_4d_conv_pg REAL, away_4d_att_pg REAL, away_top REAL, 

        away_opp_ppg REAL, away_opp_pass_comp_pg REAL, away_opp_pass_yd_pg REAL, away_opp_pass_td_pg REAL, away_opp_int_thrown_pg REAL, away_opp_sacks_taken_pg REAL, away_opp_rush_att_pg REAL, away_opp_rush_yds_pg REAL, away_opp_rush_td_pg REAL, away_opp_fgm_pg REAL, away_opp_fga_pg REAL, away_opp_pnt_pg REAL, away_opp_3d_conv_pg REAL, away_opp_3d_att_pg REAL, away_opp_4d_conv_pg REAL, away_opp_4d_att_pg REAL, away_opp_top REAL,

        home_home_game_count INTEGER, home_away_game_count INTEGER, 

        home_ppg REAL, home_pass_comp_pg REAL, home_pass_yd_pg REAL, home_pass_td_pg REAL, home_int_thrown_pg REAL, home_sacks_taken_pg REAL, home_rush_att_pg REAL, home_rush_yds_pg REAL, home_rush_td_pg REAL, home_fgm_pg REAL, home_fga_pg REAL, home_pnt_pg REAL, home_3d_conv_pg REAL, home_3d_att_pg REAL, home_4d_conv_pg REAL, home_4d_att_pg REAL, home_top REAL, 

        home_opp_ppg REAL, home_opp_pass_comp_pg REAL, home_opp_pass_yd_pg REAL, home_opp_pass_td_pg REAL, home_opp_int_thrown_pg REAL, home_opp_sacks_taken_pg REAL, home_opp_rush_att_pg REAL, home_opp_rush_yds_pg REAL, home_opp_rush_td_pg REAL, home_opp_fgm_pg REAL, home_opp_fga_pg REAL, home_opp_pnt_pg REAL, home_opp_3d_conv_pg REAL, home_opp_3d_att_pg REAL, home_opp_4d_conv_pg REAL, home_opp_4d_att_pg REAL, home_opp_top REAL,
        
        UNIQUE(year, week, away, home) ON CONFLICT IGNORE)''')

    # used create a game record and insert the spread lines, and total line into the database for that game
    def insert_line_data(self, year, week, line_data_list):
        for line_data in line_data_list:
            self._insert_new_record(year, week, line_data['away'], line_data['home'])
            self._update_line_data(line_data['away_spread'], line_data['home_spread'], line_data['total_line'], year, week, line_data['away'], line_data['home'])

    # used to update the spread lines, and total line for a given game
    def _update_line_data(self, away_spread, home_spread, total_line, year, week, away, home):
        cursor = self.conn.cursor()
        sql = f'UPDATE nfl_game_data SET away_spread={away_spread}, home_spread={home_spread}, total_line={total_line} WHERE year={year} AND week={week} AND away="{away}" AND home="{home}"'
        cursor.execute(sql)
        self.conn.commit()

    # inserts a new game record into the database
    def _insert_new_record(self, year, week, away, home):
        cursor = self.conn.cursor()
        sql = f'INSERT INTO nfl_game_data(year, week, away, home) VALUES({year}, {week}, "{away}", "{home}")'
        cursor.execute(sql)
        self.conn.commit()

    # selects records where there is a game entry but the stats are NULL and need to be added
    # returns a list of dictionaries with the information about the games: date, away team, home team
    def select_stats_needed(self):
        cursor = self.conn.cursor()
        sql = 'SELECT year, week, away, home FROM nfl_game_data WHERE away_pass_td_pg is NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        rows = result.fetchall()
        stats_needed_list = []
        for row in rows:
            row_as_dict = {
                'year': row[0],
                'week': row[1],
                'away': row[2],
                'home': row[3]}                
            stats_needed_list.append(row_as_dict)
        return stats_needed_list

    # takes a list of dictionaries with the information about games: date, away team, home team
    # also takes 2 level dictionary that contains the stats needed for all the teams in stats_needed_list
    # the function updates the records that correspond to the games in stats_needed_list with all the stats
    def insert_stats(self, stats_needed_list, stats):
        for game_data in stats_needed_list:
            year = game_data['year']
            week = game_data['week']
            away = game_data['away']
            home = game_data['home']
            away_stats = stats[away]
            home_stats = stats[home]
            cursor = self.conn.cursor()
            stat_values = (
                away_stats['home_game_count'], away_stats['away_game_count'], 
                away_stats['ppg'], away_stats['pass_comp_pg'], away_stats['pass_yd_pg'], away_stats['pass_td_pg'], away_stats['int_thrown_pg'], away_stats['sacks_taken_pg'], away_stats['rush_att_pg'], away_stats['rush_yds_pg'], away_stats['rush_td_pg'], away_stats['fgm_pg'], away_stats['fga_pg'], away_stats['pnt_pg'], away_stats['3d_conv_pg'], away_stats['3d_att_pg'], away_stats['4d_conv_pg'], away_stats['4d_att_pg'], away_stats['top'],
                away_stats['opp_ppg'], away_stats['opp_pass_comp_pg'], away_stats['opp_pass_yd_pg'], away_stats['opp_pass_td_pg'], away_stats['opp_int_thrown_pg'], away_stats['opp_sacks_taken_pg'], away_stats['opp_rush_att_pg'], away_stats['opp_rush_yds_pg'], away_stats['opp_rush_td_pg'], away_stats['opp_fgm_pg'], away_stats['opp_fga_pg'], away_stats['opp_pnt_pg'], away_stats['opp_3d_conv_pg'], away_stats['opp_3d_att_pg'], away_stats['opp_4d_conv_pg'], away_stats['opp_4d_att_pg'], away_stats['opp_top'],       
                home_stats['home_game_count'], home_stats['away_game_count'], 
                home_stats['ppg'], home_stats['pass_comp_pg'], home_stats['pass_yd_pg'], home_stats['pass_td_pg'], home_stats['int_thrown_pg'], home_stats['sacks_taken_pg'], home_stats['rush_att_pg'], home_stats['rush_yds_pg'], home_stats['rush_td_pg'], home_stats['fgm_pg'], home_stats['fga_pg'], home_stats['pnt_pg'], home_stats['3d_conv_pg'], home_stats['3d_att_pg'], home_stats['4d_conv_pg'], home_stats['4d_att_pg'], home_stats['top'],
                home_stats['opp_ppg'], home_stats['opp_pass_comp_pg'], home_stats['opp_pass_yd_pg'], home_stats['opp_pass_td_pg'], home_stats['opp_int_thrown_pg'], home_stats['opp_sacks_taken_pg'], home_stats['opp_rush_att_pg'], home_stats['opp_rush_yds_pg'], home_stats['opp_rush_td_pg'], home_stats['opp_fgm_pg'], home_stats['opp_fga_pg'], home_stats['opp_pnt_pg'], home_stats['opp_3d_conv_pg'], home_stats['opp_3d_att_pg'], home_stats['opp_4d_conv_pg'], home_stats['opp_4d_att_pg'], home_stats['opp_top'])
            sql = f'''
                UPDATE nfl_game_data SET away_home_game_count=?, away_away_game_count=?, 
        
                away_ppg=?, away_pass_comp_pg=?, away_pass_yd_pg=?, away_pass_td_pg=?, away_int_thrown_pg=?, away_sacks_taken_pg=?, away_rush_att_pg=?, away_rush_yds_pg=?, away_rush_td_pg=?, away_fgm_pg=?, away_fga_pg=?, away_pnt_pg=?, away_3d_conv_pg=?, away_3d_att_pg=?, away_4d_conv_pg=?, away_4d_att_pg=?, away_top=?, 

                away_opp_ppg=?, away_opp_pass_comp_pg=?, away_opp_pass_yd_pg=?, away_opp_pass_td_pg=?, away_opp_int_thrown_pg=?, away_opp_sacks_taken_pg=?, away_opp_rush_att_pg=?, away_opp_rush_yds_pg=?, away_opp_rush_td_pg=?, away_opp_fgm_pg=?, away_opp_fga_pg=?, away_opp_pnt_pg=?, away_opp_3d_conv_pg=?, away_opp_3d_att_pg=?, away_opp_4d_conv_pg=?, away_opp_4d_att_pg=?, away_opp_top=?,

                home_home_game_count=?, home_away_game_count=?, 

                home_ppg=?, home_pass_comp_pg=?, home_pass_yd_pg=?, home_pass_td_pg=?, home_int_thrown_pg=?, home_sacks_taken_pg=?, home_rush_att_pg=?, home_rush_yds_pg=?, home_rush_td_pg=?, home_fgm_pg=?, home_fga_pg=?, home_pnt_pg=?, home_3d_conv_pg=?, home_3d_att_pg=?, home_4d_conv_pg=?, home_4d_att_pg=?, home_top=?, 

                home_opp_ppg=?, home_opp_pass_comp_pg=?, home_opp_pass_yd_pg=?, home_opp_pass_td_pg=?, home_opp_int_thrown_pg=?, home_opp_sacks_taken_pg=?, home_opp_rush_att_pg=?, home_opp_rush_yds_pg=?, home_opp_rush_td_pg=?, home_opp_fgm_pg=?, home_opp_fga_pg=?, home_opp_pnt_pg=?, home_opp_3d_conv_pg=?, home_opp_3d_att_pg=?, home_opp_4d_conv_pg=?, home_opp_4d_att_pg=?, home_opp_top=? WHERE year={year} AND week={week} AND away="{away}" AND home="{home}"'''
            cursor.execute(sql, stat_values)
            self.conn.commit()

    # returns year and week of records so that they can be uniquely
    # identified for update
    def find_yearweeks_to_update(self):
        cursor = self.conn.cursor()
        sql = 'SELECT DISTINCT year, week FROM nfl_game_data WHERE away_score is NULL'
        result = cursor.execute(sql)
        self.conn.commit()
        
        years_weeks_list = []
        for row in result.fetchall():
            year_week_dict = {}
            year_week_dict['year'] = str(row[0])
            year_week_dict['week'] = str(row[1])
            years_weeks_list.append(year_week_dict)

        return years_weeks_list

    # game_scores_list is a list of dictionaries that have the away team, home team, away score, and home score
    # for a given date this function updates all the records for that date with final scores using game_scores_list
    def update_scores(self, year, week, game_scores_list):
        cursor = self.conn.cursor()

        for game_score_dict in game_scores_list:
            sql_away = 'UPDATE nfl_game_data SET away_score=? WHERE away=? AND year=? AND week=?'
            val_away = (game_score_dict['away_score'], game_score_dict['away'], year, week)
            cursor.execute(sql_away, val_away)

            sql_home = 'UPDATE nfl_game_data SET home_score=? WHERE home=? AND year=? AND week=?'
            val_home = (game_score_dict['home_score'], game_score_dict['home'], year, week)
            cursor.execute(sql_home, val_home)

        self.conn.commit()

    def select_all_data(self):
        cursor = self.conn.cursor()
        # sql = 'SELECT * FROM nfl_game_data WHERE away_score IS NOT NULL'
        sql = 'SELECT * FROM nfl_game_data'
        result = cursor.execute(sql)
        self.conn.commit()

        return result.fetchall()

    def select_headers(self):
        cursor = self.conn.cursor()
        sql = 'SELECT * FROM nfl_game_data LIMIT 0'
        cursor.execute(sql)
        self.conn.commit()

        return [colTup[0] for colTup in cursor.description]

    # def selectCount(self, week, year):
    #     cursor = self.conn.cursor()
    #     sql = f'SELECT COUNT(*) FROM nfl_game_data WHERE week={week} and year={year}'
    #     cursor.execute(sql)
    #     result = cursor.fetchall()
    #     self.conn.commit()

    #     return result[0][0]





            
