from selenium import webdriver
from selenium.webdriver.common.by import By

# class that uses Selenium to webscrape data from various sites and organizes it
class Data_Collection:
    def web_driver(self):
        options = webdriver.ChromeOptions()
        # options.add_argument("--headless")
        options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(options=options)
        self.last_n_games = 4

    # used to get the week and year of current default espn scoreboard
    def get_week_year(self):
        url = 'https://www.espn.com/nfl/scoreboard'
        self.web_driver()
        self.driver.get(url)

        year_el_selector = '.custom--week.is-active a'
        year_el = self.driver.find_element(By.CSS_SELECTOR, year_el_selector) 
        year = year_el.get_attribute('href').split('/')[-3]    
        
        week_el_selector = '.custom--week.is-active span'
        week_el = self.driver.find_element(By.CSS_SELECTOR, week_el_selector)
        week = week_el.text.split(' ')[-1]

        data = {}
        data['year'] = year
        data['week'] = week
        return data

    # method that uses the ESPN NFL scoreboard page of a particular week to scrape data
    # it is meant to be used to get the lines for the games on the given week before the games have started
    # it returns a list of dictionaries where each dictionary contains the away team, home team, away spread, home spread, and total spread
    def get_line_data(self, year, week):
        url = 'https://www.espn.com/nfl/scoreboard/_/week/' + week + '/year/' + year
        self.web_driver()
        self.driver.get(url)

        scoreboard_els_selector = '.Scoreboard__RowContainer'
        scoreboard_els = self.driver.find_elements(By.CSS_SELECTOR, scoreboard_els_selector)
        game_data_arr = []
        for scoreboard_el in scoreboard_els:
            record_els_selector = '.ScoreboardScoreCell__Record' # selects both overall record and home/away based record
            record_els = scoreboard_el.find_elements(By.CSS_SELECTOR, record_els_selector)
            if len(record_els) < 3: # skip if no home and away record when games played in other countries
                continue

            away_game_count = sum([int(x) for x in record_els[0].text.split('-')])
            home_game_count = sum([int(x) for x in record_els[2].text.split('-')])

            min_game_count = 4
            if(away_game_count < min_game_count or home_game_count < min_game_count): #skip if not enough games
                continue

            line_els_selector = '.VZTD.mLASH.rIczU.LNzKp.jsU.hfDkF.FoYYc.FuEs' # selects both spreads and totals
            line_els = scoreboard_el.find_elements(By.CSS_SELECTOR, line_els_selector)           
            if not line_els: # if no lines (game started already) skip to next game scoreboard
                continue

            favored_team_symbol = line_els[0].text.split(' ')[0].lower()
            spread = line_els[0].text.split(' ')[-1]
            if(spread == 'OFF'):
                continue
            total = line_els[1].text

            team_els_selector = '.ScoreCell__team_name.ScoreCell__team_name--shortDisplayName'
            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_els_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            team_name_to_symbol = {'bills':'buf','jets':'nyj','dolphins':'mia','patriots':'ne','steelers':'pit','ravens':'bal','bengals':'cin','browns':'cle','texans':'hou','colts':'ind','jaguars':'jax','titans':'ten','chiefs':'kc','broncos':'den','chargers':'lac','raiders':'lv','commanders':'wsh','eagles':'phi','cowboys':'dal','giants':'nyg','lions':'det','packers':'gb','vikings':'min','bears':'chi','falcons':'atl','buccaneers':'tb','saints':'no','panthers':'car','cardinals':'ari','49ers':'sf','seahawks':'sea','rams':'lar'}
            if favored_team_symbol == team_name_to_symbol[home_team]:
                home_spread = spread
            else:
                home_spread = str(float(spread) * -1)

            game_data = {}
            game_data['away'] = away_team
            game_data['home'] = home_team
            game_data['away_spread'] = str(float(home_spread) * -1)
            game_data['home_spread'] = home_spread
            game_data['total_line'] = total
            game_data_arr.append(game_data)

        return game_data_arr

    # uses pro football reference to get stats for all teams for given year
    def get_stats(self, year):
        profbref_symbols = ['buf','mia','nwe','nyj','pit','rav','cin','cle','htx','clt','jax','oti','kan','den','sdg','rai','was','phi','dal','nyg','atl','tam','nor','car','det','gnb','min','chi','crd','sea','sfo','ram']
        self.web_driver()
        stats_data = {}
        for team_symbol in profbref_symbols:
            url = 'https://www.pro-football-reference.com/teams/' + team_symbol + '/' + year + '/gamelog/'
            self.driver.get(url)

            team_name_el_selector = 'div[data-template="Partials/Teams/Summary"] h1 span'
            team_name = self.driver.find_elements(By.CSS_SELECTOR, team_name_el_selector)[1].text.split(' ')[-1].lower()

            table_el_selector = '#gamelog2024'
            keys = ['location','opponent','tm','opp','cmp','p_att','p_yds','p_td','int','sk','sk_yds','p_y/a','ny/a','cmp%','rate','r_att','r_yds','r_y/a','r_td','fgm','fga','xpm','xpa','pnt','pnt_yds','3dconv','3datt','4dconv','4datt','top']            
            team_log_data = self._get_gamelog_stats(table_el_selector, keys)
            opptable_el_selector = '#gamelog_opp2024'
            opp_keys = ['location','opponent','tm','opp','opp_cmp','opp_p_att','opp_p_yds','opp_p_td','opp_int','opp_sk','opp_sk_yds','opp_p_y/a','opp_ny/a','opp_cmp%','opp_rate','opp_r_att','opp_r_yds','opp_r_y/a','opp_r_td','opp_fgm','opp_fga','opp_xpm','opp_xpa','opp_pnt','opp_pnt_yds','opp_3dconv','opp_3datt','opp_4dconv','opp_4datt','opp_top']
            opp_log_data = self._get_gamelog_stats(opptable_el_selector, opp_keys)
            if team_log_data == None or opp_log_data == None: # skip this team if there weren't enough games worth of stats
                continue
            team_stats = {}
            away_game_count = 0
            for location in team_log_data['location']:
                if location == '@':
                    away_game_count += 1
            home_game_count = self.last_n_games - away_game_count
            team_stats['away_game_count'] = away_game_count
            team_stats['home_game_count'] = home_game_count
            team_stats['ppg'] = sum(team_log_data['tm']) / self.last_n_games   
            team_stats['pass_comp_pg'] = sum(team_log_data['cmp']) / self.last_n_games
            team_stats['pass_att_pg'] = sum(team_log_data['p_att']) / self.last_n_games
            team_stats['pass_yd_pg'] = sum(team_log_data['p_yds']) / self.last_n_games
            team_stats['pass_td_pg'] = sum(team_log_data['p_td']) / self.last_n_games
            team_stats['int_thrown_pg'] = sum(team_log_data['int']) / self.last_n_games
            team_stats['sacks_taken_pg'] = sum(team_log_data['sk']) / self.last_n_games
            team_stats['rush_att_pg'] = sum(team_log_data['r_att']) / self.last_n_games
            team_stats['rush_yds_pg'] = sum(team_log_data['r_yds']) / self.last_n_games
            team_stats['rush_td_pg'] = sum(team_log_data['r_td']) / self.last_n_games
            team_stats['fgm_pg'] = sum(team_log_data['fgm']) / self.last_n_games
            team_stats['fga_pg'] = sum(team_log_data['fga']) / self.last_n_games
            team_stats['pnt_pg'] = sum(team_log_data['pnt']) / self.last_n_games
            team_stats['3d_conv_pg'] = sum(team_log_data['3dconv']) / self.last_n_games
            team_stats['3d_att_pg'] = sum(team_log_data['3datt']) / self.last_n_games
            team_stats['4d_conv_pg'] = sum(team_log_data['4dconv']) / self.last_n_games
            team_stats['4d_att_pg'] = sum(team_log_data['4datt']) / self.last_n_games
            top_sum = 0
            for top in team_log_data['top']:
                seconds = int(top.split(':')[-1])/60
                minutes = int(top.split(':')[0]) + seconds
                top_sum += minutes
            team_stats['top'] = round(top_sum / self.last_n_games, 2)
         
            team_stats['opp_ppg'] = sum(opp_log_data['opp']) / self.last_n_games
            team_stats['opp_pass_comp_pg'] = sum(opp_log_data['opp_cmp']) / self.last_n_games
            team_stats['opp_pass_att_pg'] = sum(opp_log_data['opp_p_att']) / self.last_n_games
            team_stats['opp_pass_yd_pg'] = sum(opp_log_data['opp_p_yds']) / self.last_n_games
            team_stats['opp_pass_td_pg'] = sum(opp_log_data['opp_p_td']) / self.last_n_games
            team_stats['opp_int_thrown_pg'] = sum(opp_log_data['opp_int']) / self.last_n_games
            team_stats['opp_sacks_taken_pg'] = sum(opp_log_data['opp_sk']) / self.last_n_games
            team_stats['opp_rush_att_pg'] = sum(opp_log_data['opp_r_att']) / self.last_n_games
            team_stats['opp_rush_yds_pg'] = sum(opp_log_data['opp_r_yds']) / self.last_n_games
            team_stats['opp_rush_td_pg'] = sum(opp_log_data['opp_r_td']) / self.last_n_games
            team_stats['opp_fgm_pg'] = sum(opp_log_data['opp_fgm']) / self.last_n_games
            team_stats['opp_fga_pg'] = sum(opp_log_data['opp_fga']) / self.last_n_games
            team_stats['opp_pnt_pg'] = sum(opp_log_data['opp_pnt']) / self.last_n_games
            team_stats['opp_3d_conv_pg'] = sum(opp_log_data['opp_3dconv']) / self.last_n_games
            team_stats['opp_3d_att_pg'] = sum(opp_log_data['opp_3datt']) / self.last_n_games
            team_stats['opp_4d_conv_pg'] = sum(opp_log_data['opp_4dconv']) / self.last_n_games
            team_stats['opp_4d_att_pg'] = sum(opp_log_data['opp_4datt']) / self.last_n_games
            opptop_sum = 0
            for top in opp_log_data['opp_top']:
                seconds = int(top.split(':')[-1])/60
                minutes = int(top.split(':')[0]) + seconds
                opptop_sum += minutes
            team_stats['opp_top'] = round(opptop_sum / self.last_n_games, 2)

            stats_data[team_name] = team_stats

        return stats_data

    # helper function so I don't have to duplicate code for team and opponent     
    def _get_gamelog_stats(self, gameLogtable_el_selector, keys):
        gamelog_table_el = self.driver.find_element(By.CSS_SELECTOR, gameLogtable_el_selector)
        gamelog_tablerow_els = gamelog_table_el.find_elements(By.CSS_SELECTOR, 'tr')[2:] # remove first two rows with no game logs
        gamelog_tablerow_els.reverse() # reverse so I can stop after having data from last 4 game logs

        gamelog_data = {}
        for key in keys:
            gamelog_data[key] = []

        log_count = 0
        for row_el in gamelog_tablerow_els:
            outcome_el_selector = 'td[data-stat="game_outcome"]'
            outcome = row_el.find_element(By.CSS_SELECTOR, outcome_el_selector).text.lower()
            if outcome != 'w' and outcome != 'l': # skip log if there is no game outcome
                continue

            log_value_els = row_el.find_elements(By.CSS_SELECTOR, 'td')[5:] # remove rows without stats
            for i in range(len(log_value_els)):
                if(keys[i] == 'top' or keys[i] == 'opp_top' or keys[i] == 'location' or keys[i] == 'opponent'):
                    gamelog_data[keys[i]].append(log_value_els[i].text)
                else:
                    gamelog_data[keys[i]].append(float(log_value_els[i].text))
            
            log_count +=1
            if log_count == self.last_n_games:
                break

        if log_count != self.last_n_games: # return None if not enough game so I can't insert stats in the database later
            return None

        return gamelog_data

    # method goes to ESPN NFL scoredboard page for given week and 
    # year and retrieves the teams and scores for each
    # returns list of dictionaries [{away: away team, home: home 
    # team, away_score: away score, home_score: home score}, ...]
    # date format is 'yyyymmdd'
    def retrieve_scores(self, year, week):
        url = 'https://www.espn.com/nfl/scoreboard/_/week/' + week + '/year/' + year
        team_selector = '.ScoreCell__team_name.ScoreCell__team_name--shortDisplayName'
        score_selector = '.ScoreCell__Score.ScoreCell_Score--scoreboard'
        scoreboard_selector = '.Scoreboard__RowContainer'
        progress_selector = '.ScoreCell__Time'

        self.web_driver()
        self.driver.get(url)

        scoreboard_els = self.driver.find_elements(By.CSS_SELECTOR, scoreboard_selector)
    
        score_data = []
        for scoreboard_el in scoreboard_els:
            # the following checks if the game is finished before collecting the scores
            game_progress = scoreboard_el.find_element(By.CSS_SELECTOR, progress_selector).text.split('/')[0].lower()
            if(game_progress != 'final'):
                continue

            team_els = scoreboard_el.find_elements(By.CSS_SELECTOR, team_selector)
            away_team = team_els[0].text.split(' ')[-1].lower()
            home_team = team_els[1].text.split(' ')[-1].lower()

            score_els = scoreboard_el.find_elements(By.CSS_SELECTOR, score_selector)
            away_score = score_els[0].text
            home_score = score_els[1].text

            game_data = {}
            game_data['away'] = away_team
            game_data['home'] = home_team
            game_data['away_score'] = away_score
            game_data['home_score'] = home_score
            score_data.append(game_data)

        return score_data






        



        
