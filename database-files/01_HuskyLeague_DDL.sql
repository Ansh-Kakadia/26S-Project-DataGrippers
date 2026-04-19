DROP DATABASE IF EXISTS HuskyLeague;
CREATE DATABASE HuskyLeague;
USE HuskyLeague;

CREATE TABLE League
(
    season             INT                                           NOT NULL,
    skill_level        ENUM ('Beginner', 'Intermediate', 'Advanced') NOT NULL,
    registration_start DATETIME                                      NOT NULL,
    registration_end   DATETIME                                      NOT NULL,
    rules              VARCHAR(1000)                                 NOT NULL,
    status             ENUM ('Active', 'Pending', 'Finished')        NOT NULL,
    schedule_type      ENUM ('Round Robin', 'Elimination')           NOT NULL,
    roster_limit       INT                                           NOT NULL,
    division_tier      INT                                           NOT NULL,
    sport              VARCHAR(50)                                   NOT NULL,
    league_name        VARCHAR(50)                                   NOT NULL,
    id                 INT PRIMARY KEY AUTO_INCREMENT
);

CREATE TABLE Player
(
    id                INT PRIMARY KEY NOT NULL AUTO_INCREMENT,
    first_name        VARCHAR(45)     NOT NULL,
    last_name         VARCHAR(45)     NOT NULL,
    email             VARCHAR(100)    NOT NULL UNIQUE,
    phone             VARCHAR(20),
    university        VARCHAR(100),
    notification_pref ENUM ('Subscribed', 'Unsubscribed'),
    graduation_year   INT
);

CREATE TABLE Team
(
    name       VARCHAR(50)                    NOT NULL,
    status     ENUM ('Active', 'Inactive')    NOT NULL,
    id         INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    captain_id INT                            NOT NULL,
    league_id  INT                            NOT NULL,
    CONSTRAINT captain_team_fk
        FOREIGN KEY (captain_id)
            REFERENCES Player (id),
    CONSTRAINT league_team_fk
        FOREIGN KEY (league_id)
            REFERENCES League (id)
);

CREATE TABLE Analytics_Report
(
    id                     INT PRIMARY KEY AUTO_INCREMENT,
    season                 INT            NOT NULL,
    sport                  VARCHAR(50)    NOT NULL,
    generated_date         DATETIME       NOT NULL,
    data                   VARCHAR(10000) NOT NULL,
    recommendations        VARCHAR(500)   NOT NULL,
    team_being_analyzed_id INT            NOT NULL,
    CONSTRAINT anal_team_rep
        FOREIGN KEY (team_being_analyzed_id)
            REFERENCES Team (id)
);

CREATE TABLE Team_Message
(
    team_id   INT          NOT NULL,
    sent_at   DATETIME     NOT NULL,
    player_id INT          NOT NULL,
    id        INT PRIMARY KEY AUTO_INCREMENT,
    message   VARCHAR(500) NOT NULL,
    CONSTRAINT team_message_team_id
        FOREIGN KEY (team_id)
            REFERENCES Team (id),
    CONSTRAINT team_message_player_id
        FOREIGN KEY (player_id)
            REFERENCES Player (id)
);

CREATE TABLE Team_Membership
(
    date_joined DATETIME,
    designation VARCHAR(100),
    status      ENUM ('Active', 'Inactive'),
    team_id     INT NOT NULL,
    player_id   INT NOT NULL,
    role        ENUM ('Captain', 'Player'),
    join_method ENUM ('Invite', 'Search'),
    id          INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT Team_MEM_Player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT Team_MEM_TEAM
        FOREIGN KEY (team_id)
            REFERENCES Team (id)
);

CREATE TABLE Venue
(
    address    VARCHAR(200) UNIQUE NOT NULL,
    sport_type VARCHAR(50)         NOT NULL,
    capacity   INT                 NOT NULL,
    id         INT PRIMARY KEY AUTO_INCREMENT,
    name       VARCHAR(200)        NOT NULL
);

CREATE TABLE Venue_Time_Slot
(
    id              INT PRIMARY KEY AUTO_INCREMENT,
    venue_id        INT      NOT NULL,
    league_id       INT      NOT NULL,
    slot_date       DATETIME NOT NULL,
    slot_start_time DATETIME NOT NULL,
    slot_end_time   DATETIME NOT NULL,
    is_available    BOOLEAN  NOT NULL,
    CONSTRAINT venue_ts_venue
        FOREIGN KEY (venue_id)
            REFERENCES Venue (id),
    CONSTRAINT venue_ts_league
        FOREIGN KEY (league_id)
            REFERENCES League (id)
);

CREATE TABLE Game
(
    game_time          DATETIME                                              NOT NULL,
    venue_id           INT                                                   NOT NULL,
    game_date          DATETIME                                              NOT NULL,
    status             ENUM ('Pending', 'Canceled', 'Rescheduled',
                             'Active', 'Completed')                          NOT NULL,
    venue_time_slot_id INT                                                   NOT NULL,
    away_team_id       INT                                                   NOT NULL,
    home_team_id       INT                                                   NOT NULL,
    league_id          INT                                                   NOT NULL,
    id                 INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT game_venue
        FOREIGN KEY (venue_id)
            REFERENCES Venue (id),
    CONSTRAINT game_venue_time_slot
        FOREIGN KEY (venue_time_slot_id)
            REFERENCES Venue_Time_Slot (id),
    CONSTRAINT away_team
        FOREIGN KEY (away_team_id)
            REFERENCES Team (id),
    CONSTRAINT home_team
        FOREIGN KEY (home_team_id)
            REFERENCES Team (id),
    CONSTRAINT game_league
        FOREIGN KEY (league_id)
            REFERENCES League (id)
);

CREATE TABLE Dispute
(
    admin_notes          VARCHAR(200),
    game_id              INT                             NOT NULL,
    submitted_by_team_id INT                             NOT NULL,
    dispute_type         ENUM ('Score Dispute', 'Other') NOT NULL,
    status               ENUM ('Pending', 'Resolved')    NOT NULL,
    description          VARCHAR(1000)                   NOT NULL,
    resolution           VARCHAR(500),
    resolution_date      DATETIME,
    is_resolved          BOOLEAN                         NOT NULL,
    id                   INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT game_dispute
        FOREIGN KEY (game_id)
            REFERENCES Game (id),
    CONSTRAINT dispute_submission
        FOREIGN KEY (submitted_by_team_id)
            REFERENCES Team (id)
);

CREATE TABLE Game_Result
(
    game_id         INT     NOT NULL,
    winning_team_id INT     NOT NULL,
    home_score      INT     NOT NULL,
    away_score      INT     NOT NULL,
    is_forfeit      BOOLEAN NOT NULL,
    id              INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT result_game
        FOREIGN KEY (game_id)
            REFERENCES Game (id),
    CONSTRAINT winning_team_id FOREIGN KEY (winning_team_id)
        REFERENCES Team (id)
);

CREATE TABLE Venue_Review
(
    field_quality_rating INT,
    venue_id             INT      NOT NULL,
    player_id            INT,
    game_id              INT,
    lighting_rating      INT,
    text                 VARCHAR(500),
    parking_rating       INT,
    overall_rating       INT      NOT NULL,
    last_reviewed_date   DATETIME NOT NULL,
    id                   INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT review_venue
        FOREIGN KEY (venue_id)
            REFERENCES Venue (id),
    CONSTRAINT review_player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT review_game
        FOREIGN KEY (game_id)
            REFERENCES Game (id)
);

CREATE TABLE Notification
(
    id                INT PRIMARY KEY AUTO_INCREMENT,
    is_read           BOOLEAN                  NOT NULL,
    sent_at           DATETIME                 NOT NULL,
    message           VARCHAR(200)             NOT NULL,
    game_id           INT,
    player_id         INT                      NOT NULL,
    league_id         INT,
    notification_type ENUM ('Email', 'Banner') NOT NULL,
    CONSTRAINT notif_game
        FOREIGN KEY (game_id)
            REFERENCES Game (id),
    CONSTRAINT notif_player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT notif_league
        FOREIGN KEY (league_id)
            REFERENCES League (id)
);

CREATE TABLE Score_Submission
(
    player_id       INT                          NOT NULL,
    game_id         INT                          NOT NULL,
    home_score      INT                          NOT NULL,
    away_score      INT                          NOT NULL,
    status          ENUM ('Reviewed', 'Pending') NOT NULL,
    submission_date DATETIME                     NOT NULL,
    dispute_reason  VARCHAR(200)                 NOT NULL,
    is_disputed     BOOLEAN                      NOT NULL,
    id              INT AUTO_INCREMENT PRIMARY KEY,
    CONSTRAINT score_sub_player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT score_sub_game
        FOREIGN KEY (game_id)
            REFERENCES Game (id)
);

CREATE TABLE Player_Game_Stats
(
    points       INT,
    goals_scored INT,
    player_id    INT     NOT NULL,
    game_id      INT     NOT NULL,
    assists      INT,
    attended     BOOLEAN NOT NULL,
    wins         INT     NOT NULL,
    id           INT PRIMARY KEY AUTO_INCREMENT,
    CONSTRAINT stats_player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT stats_game
        FOREIGN KEY (game_id)
            REFERENCES Game (id)
);

CREATE TABLE Free_Agent_Request
(
    id              INT PRIMARY KEY AUTO_INCREMENT,
    status          ENUM ('Accepted', 'Rejected', 'Pending')    NOT NULL,
    player_id       INT                                         NOT NULL,
    league_id       INT                                         NOT NULL,
    request_date    DATETIME                                    NOT NULL,
    CONSTRAINT agent_req_player
        FOREIGN KEY (player_id)
            REFERENCES Player (id),
    CONSTRAINT agent_req_league
        FOREIGN KEY (league_id)
            REFERENCES League (id)
);


USE HuskyLeague;

INSERT INTO League (season, skill_level, registration_start, registration_end, rules, status, schedule_type,
                    roster_limit, division_tier, sport, league_name)
VALUES (2025, 'Beginner', '2025-01-01 09:00:00', '2025-01-15 23:59:00',
        'Standard intramural soccer rules apply. No slide tackling. Sportsmanship required.', 'Finished', 'Round Robin',
        12, 1, 'Soccer', 'Fall Soccer Beginners'),
       (2025, 'Intermediate', '2025-01-01 09:00:00', '2025-01-15 23:59:00',
        'Standard intramural basketball rules. 5-on-5 format. No dunking on breakaway.', 'Finished', 'Round Robin', 10,
        2, 'Basketball', 'Fall Basketball Intermediate'),
       (2026, 'Advanced', '2026-03-01 09:00:00', '2026-03-20 23:59:00',
        'Competitive volleyball rules. Best of 3 sets. Rally scoring to 25.', 'Active', 'Elimination', 8, 1,
        'Volleyball', 'Spring Volleyball Advanced');

INSERT INTO Player (first_name, last_name, email, phone, university, notification_pref, graduation_year)
VALUES ('Marcus', 'Rivera', 'marcus.rivera@husky.neu.edu', '617-555-0101', 'Northeastern University', 'Subscribed',
        2026),
       ('Priya', 'Nair', 'priya.nair@husky.neu.edu', '617-555-0202', 'Northeastern University', 'Subscribed', 2027),
       ('Jordan', 'Blake', 'jordan.blake@husky.neu.edu', '617-555-0303', 'Northeastern University', 'Unsubscribed',
        2025),
       ('Sofia', 'Chen', 'sofia.chen@husky.neu.edu', '617-555-0404', 'Northeastern University', 'Subscribed', 2026),
       ('DeShawn', 'Williams', 'deshawn.w@husky.neu.edu', '617-555-0505', 'Northeastern University', 'Subscribed',
        2027);

INSERT INTO Team (name, status, captain_id, league_id)
VALUES ('Red Storm', 'Active', 1, 1),
       ('Blue Thunder', 'Active', 2, 2),
       ('Gold Spikers', 'Active', 4, 3);

INSERT INTO Analytics_Report (season, sport, generated_date, data, recommendations, team_being_analyzed_id)
VALUES (2025, 'Soccer', '2025-03-01 10:00:00',
        '{"wins":4,"losses":1,"goals_for":14,"goals_against":6,"avg_possession":58}',
        'Maintain possession-based play. Work on defensive transitions.', 1),
       (2025, 'Basketball', '2025-03-01 10:30:00',
        '{"wins":3,"losses":2,"points_per_game":52,"opponent_ppg":48,"turnovers_per_game":9}',
        'Reduce turnovers in the second half. Improve three-point defense.', 2),
       (2026, 'Volleyball', '2026-03-25 11:00:00',
        '{"wins":1,"losses":0,"sets_won":3,"sets_lost":1,"aces":12,"service_errors":5}',
        'Capitalize on strong serve. Reduce service error rate below 10%.', 3);


INSERT INTO Team_Message (team_id, sent_at, player_id, message)
VALUES (1, '2025-02-10 14:22:00', 1, 'Practice moved to Tuesday at 6pm. Lets get ready for the game!'),
       (2, '2025-02-11 09:05:00', 2, 'Reminder: wear your blue jerseys for the next game.'),
       (3, '2026-03-22 18:45:00', 4, 'Great first win everyone! Keep the energy up for next week.');

INSERT INTO Team_Membership (date_joined, designation, status, team_id, player_id, role, join_method)
VALUES ('2025-01-16 10:00:00', 'Starter', 'Active', 1, 1, 'Captain', 'Search'),
       ('2025-01-17 11:00:00', 'Starter', 'Active', 1, 3, 'Player', 'Invite'),
       ('2025-01-16 10:30:00', 'Starter', 'Active', 2, 2, 'Captain', 'Search'),
       ('2025-01-18 12:00:00', 'Substitute', 'Active', 2, 5, 'Player', 'Search'),
       ('2026-03-21 09:00:00', 'Starter', 'Active', 3, 4, 'Captain', 'Search');

INSERT INTO Venue (address, sport_type, capacity, name)
VALUES ('360 Huntington Ave, Boston, MA 02115', 'Soccer', 200, 'Parsons Field'),
       ('219 St. Botolph St, Boston, MA 02115', 'Basketball', 150, 'Cabot Gym Court A'),
       ('40 Leon St, Boston, MA 02115', 'Volleyball', 100, 'Marino Rec Volleyball Court');

INSERT INTO Venue_Time_Slot (venue_id, league_id, slot_date, slot_start_time, slot_end_time, is_available)
VALUES (1, 1, '2025-02-15 00:00:00', '2025-02-15 18:00:00', '2025-02-15 20:00:00', FALSE),
       (2, 2, '2025-02-16 00:00:00', '2025-02-16 19:00:00', '2025-02-16 21:00:00', FALSE),
       (3, 3, '2026-04-05 00:00:00', '2026-04-05 17:00:00', '2026-04-05 19:00:00', TRUE);

INSERT INTO Game (game_time, venue_id, game_date, status, venue_time_slot_id, away_team_id, home_team_id, league_id)
VALUES ('2025-02-15 18:00:00', 1, '2025-02-15 00:00:00', 'Active', 1, 2, 1, 1),
       ('2025-02-16 19:00:00', 2, '2025-02-16 00:00:00', 'Active', 2, 1, 2, 2),
       ('2026-04-05 17:00:00', 3, '2026-04-05 00:00:00', 'Pending', 3, 1, 3, 3);

INSERT INTO Dispute (admin_notes, game_id, submitted_by_team_id, dispute_type, status, description, resolution,
                     resolution_date, is_resolved)
VALUES ('Reviewed video footage. Score confirmed.', 1, 2, 'Score Dispute', 'Resolved',
        'Away team believes the final score was recorded incorrectly. Claimed 3-2 not 2-2.',
        'Original score upheld after video review.', '2025-02-17 10:00:00', TRUE),
       (NULL, 2, 1, 'Other', 'Pending',
        'Home team arrived 10 minutes late causing a delayed start. Away team requests forfeit.', NULL, NULL, FALSE);

INSERT INTO Game_Result (game_id, winning_team_id, home_score, away_score, is_forfeit)
VALUES (1, 1, 3, 1, FALSE),
       (2, 2, 4, 2, FALSE);

INSERT INTO Venue_Review (field_quality_rating, venue_id, player_id, game_id, lighting_rating, text, parking_rating,
                          overall_rating, last_reviewed_date)
VALUES (4, 1, 1, 1, 5, 'Great field, very well lit for an evening game. Parking was a bit tight.', 3, 4,
        '2025-02-15 21:00:00'),
       (3, 2, 2, 2, 4, 'Court was clean and well maintained. Could use better seating for spectators.', 4, 4,
        '2025-02-16 22:00:00'),
       (5, 1, 3, 1, 5, 'Best field we have played on all season. No complaints.', 3, 5, '2025-02-15 21:30:00');

INSERT INTO Notification (is_read, sent_at, message, game_id, player_id, league_id, notification_type)
VALUES (TRUE, '2025-02-14 09:00:00', 'Reminder: Your game vs Blue Thunder is tomorrow at 6pm at Parsons Field.', 1, 1,
        1, 'Email'),
       (FALSE, '2025-02-15 20:30:00', 'Game result posted: Red Storm 3 - Blue Thunder 1.', 1, 3, 1, 'Banner'),
       (FALSE, '2026-03-25 08:00:00', 'Your next match has been scheduled for April 5th at Marino Rec.', 3, 4, 3,
        'Email');

INSERT INTO Score_Submission (player_id, game_id, home_score, away_score, status, submission_date, dispute_reason,
                              is_disputed)
VALUES (1, 1, 3, 1, 'Reviewed', '2025-02-15 20:15:00', '', FALSE),
       (2, 1, 2, 2, 'Reviewed', '2025-02-15 20:20:00', 'One goal was scored after the final whistle blew.', TRUE),
       (3, 2, 4, 2, 'Pending', '2025-02-16 21:10:00', '', FALSE);

INSERT INTO Player_Game_Stats (points, goals_scored, player_id, game_id, assists, attended, wins)
VALUES (NULL, 2, 1, 1, 1, TRUE, 1),
       (NULL, 0, 3, 1, 2, TRUE, 1),
       (12, NULL, 2, 2, 3, TRUE, 0),
       (8, NULL, 5, 2, 1, TRUE, 0),
       (NULL, 0, 4, 1, 0, FALSE, 0);

INSERT INTO Free_Agent_Request (status, player_id, league_id, request_date)
VALUES ('Accepted', 1, 1, '2025-01-01 08:00:00'),
       ('Rejected', 5, 3, '2026-01-06 14:42:59'),
       ('Pending', 3, 3, '2026-01-10 20:01:32')

USE HuskyLeague;

INSERT INTO League (season, skill_level, registration_start, registration_end, rules, status, schedule_type, roster_limit, division_tier, sport, league_name) VALUES
(2025, 'Advanced',     '2025-01-01 09:00:00', '2025-01-15 23:59:00', 'Competitive soccer. Yellow and red cards enforced. Full 90-minute matches.', 'Finished',  'Elimination', 10, 3, 'Soccer',        'Fall Soccer Advanced'),
(2025, 'Beginner',     '2025-01-01 09:00:00', '2025-01-15 23:59:00', 'Beginner basketball. No hard contact. Fun and learning focused.', 'Finished',              'Round Robin', 12, 1, 'Basketball',    'Fall Basketball Beginners'),
(2026, 'Beginner',     '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Basic volleyball. Best of 3 sets. Beginner friendly environment.', 'Active',               'Round Robin', 10, 1, 'Volleyball',    'Spring Volleyball Beginner'),
(2026, 'Intermediate', '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Standard soccer. 7-on-7 format. Fair play strictly required.', 'Active',                   'Round Robin', 14, 2, 'Soccer',        'Spring Soccer Intermediate'),
(2025, 'Intermediate', '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Standard flag football rules. No contact of any kind allowed.', 'Finished',               'Round Robin', 10, 2, 'Flag Football', 'Summer Flag Football Intermediate'),
(2025, 'Advanced',     '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Competitive tennis doubles. Best of 3 sets. USTA scoring rules.', 'Finished',             'Elimination', 6,  3, 'Tennis',        'Summer Tennis Advanced'),
(2026, 'Beginner',     '2026-01-10 09:00:00', '2026-01-25 23:59:00', 'Basic badminton. Single elimination bracket. Beginner pace.', 'Finished',                 'Elimination', 8,  1, 'Badminton',     'Winter Badminton Beginner'),
(2026, 'Intermediate', '2026-01-10 09:00:00', '2026-01-25 23:59:00', 'Standard table tennis. Rally scoring to 11 points per game.', 'Finished',                 'Round Robin', 8,  2, 'Table Tennis',  'Winter Table Tennis Intermediate'),
(2025, 'Beginner',     '2025-09-01 09:00:00', '2025-09-15 23:59:00', 'Basic ultimate frisbee. Non-contact. Spirit of the game required.', 'Finished',           'Round Robin', 10, 1, 'Frisbee',       'Fall Frisbee Beginners'),
(2025, 'Advanced',     '2025-09-01 09:00:00', '2025-09-15 23:59:00', 'Competitive frisbee. Mixed gender teams strongly encouraged.', 'Finished',                 'Elimination', 10, 3, 'Frisbee',       'Fall Frisbee Advanced'),
(2026, 'Advanced',     '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Competitive basketball. Full court. 5-on-5. NFHS ruleset applies.', 'Active',              'Elimination', 10, 3, 'Basketball',    'Spring Basketball Advanced'),
(2026, 'Beginner',     '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Basic soccer. 5-on-5. No pressure. Fun and inclusive environment.', 'Pending',             'Round Robin', 10, 1, 'Soccer',        'Spring Soccer Beginners'),
(2025, 'Intermediate', '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Standard volleyball. Best of 5 sets. Co-ed teams welcome.', 'Finished',                    'Round Robin', 10, 2, 'Volleyball',    'Summer Volleyball Intermediate'),
(2025, 'Beginner',     '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Beginner tennis singles. No advantage scoring. Relaxed format.', 'Finished',              'Elimination', 8,  1, 'Tennis',        'Summer Tennis Beginner'),
(2026, 'Advanced',     '2026-01-10 09:00:00', '2026-01-25 23:59:00', 'Competitive flag football. 8-on-8. No contact permitted.', 'Finished',                     'Elimination', 8,  3, 'Flag Football', 'Winter Flag Football Advanced'),
(2026, 'Intermediate', '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Standard frisbee. Mixed gender teams required every game.', 'Active',                      'Round Robin', 10, 2, 'Frisbee',       'Spring Frisbee Intermediate'),
(2025, 'Advanced',     '2025-01-01 09:00:00', '2025-01-15 23:59:00', 'Competitive badminton. Best of 3 games. Singles bracket format.', 'Finished',              'Elimination', 6,  3, 'Badminton',     'Fall Badminton Advanced'),
(2025, 'Intermediate', '2025-09-01 09:00:00', '2025-09-15 23:59:00', 'Standard basketball. Half-court. 3-on-3. Intermediate level.', 'Finished',                'Round Robin', 8,  2, 'Basketball',    'Fall Basketball Half-Court'),
(2026, 'Beginner',     '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Basic flag football. Touch only. No tackles or grabs permitted.', 'Pending',               'Round Robin', 12, 1, 'Flag Football', 'Spring Flag Football Beginners'),
(2025, 'Advanced',     '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Competitive soccer. Full field. 11-on-11 regulation play.', 'Finished',                    'Elimination', 15, 3, 'Soccer',        'Summer Soccer Advanced'),
(2025, 'Beginner',     '2025-09-01 09:00:00', '2025-09-15 23:59:00', 'Basic volleyball. 6-on-6. Beginner friendly. Emphasis on fun.', 'Finished',                'Round Robin', 12, 1, 'Volleyball',    'Fall Volleyball Beginner'),
(2026, 'Intermediate', '2026-01-10 09:00:00', '2026-01-25 23:59:00', 'Standard soccer. 7-on-7 format. Intermediate players only.', 'Finished',                   'Round Robin', 14, 2, 'Soccer',        'Winter Soccer Intermediate'),
(2025, 'Intermediate', '2025-01-01 09:00:00', '2025-01-15 23:59:00', 'Standard frisbee. Mixed format permitted. Spirit points tracked.', 'Finished',             'Round Robin', 10, 2, 'Frisbee',       'Fall Frisbee Intermediate'),
(2026, 'Advanced',     '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Competitive tennis singles. Full USTA tournament scoring.', 'Active',                      'Elimination', 6,  3, 'Tennis',        'Spring Tennis Advanced'),
(2025, 'Beginner',     '2025-06-01 09:00:00', '2025-06-15 23:59:00', 'Basic basketball. 3-on-3. Beginner level. Relaxed and fun.', 'Finished',                   'Round Robin', 6,  1, 'Basketball',    'Summer Basketball 3v3'),
(2026, 'Intermediate', '2026-03-01 09:00:00', '2026-03-20 23:59:00', 'Standard badminton. Doubles format required every match.', 'Active',                       'Round Robin', 8,  2, 'Badminton',     'Spring Badminton Intermediate'),
(2025, 'Advanced',     '2025-09-01 09:00:00', '2025-09-15 23:59:00', 'Competitive table tennis. Single elimination. Seeded bracket.', 'Finished',               'Elimination', 8,  3, 'Table Tennis',  'Fall Table Tennis Advanced');


INSERT INTO Player (first_name, last_name, email, phone, university, notification_pref, graduation_year) VALUES
('Alex',      'Thompson',  'alex.thompson@husky.neu.edu',      '617-555-0106', 'Northeastern University', 'Subscribed',   2026),
('Maya',      'Patel',     'maya.patel@husky.neu.edu',         '617-555-0107', 'Northeastern University', 'Subscribed',   2027),
('Ethan',     'Kim',       'ethan.kim@husky.neu.edu',          '617-555-0108', 'Northeastern University', 'Unsubscribed', 2025),
('Olivia',    'Martinez',  'olivia.martinez@husky.neu.edu',    '617-555-0109', 'Northeastern University', 'Subscribed',   2026),
('Noah',      'Johnson',   'noah.johnson@husky.neu.edu',       '617-555-0110', 'Northeastern University', 'Subscribed',   2028),
('Ava',       'Garcia',    'ava.garcia@husky.neu.edu',         '617-555-0111', 'Northeastern University', 'Unsubscribed', 2026),
('Liam',      'Lee',       'liam.lee@husky.neu.edu',           '617-555-0112', 'Northeastern University', 'Subscribed',   2027),
('Emma',      'Wilson',    'emma.wilson@husky.neu.edu',        '617-555-0113', 'Northeastern University', 'Subscribed',   2025),
('James',     'Anderson',  'james.anderson@husky.neu.edu',     '617-555-0114', 'Northeastern University', 'Subscribed',   2026),
('Isabella',  'Taylor',    'isabella.taylor@husky.neu.edu',    '617-555-0115', 'Northeastern University', 'Unsubscribed', 2027),
('Oliver',    'Brown',     'oliver.brown@husky.neu.edu',       '617-555-0116', 'Northeastern University', 'Subscribed',   2028),
('Mia',       'Davis',     'mia.davis@husky.neu.edu',          '617-555-0117', 'Northeastern University', 'Subscribed',   2026),
('Benjamin',  'Miller',    'benjamin.miller@husky.neu.edu',    '617-555-0118', 'Northeastern University', 'Subscribed',   2025),
('Charlotte', 'Moore',     'charlotte.moore@husky.neu.edu',    '617-555-0119', 'Northeastern University', 'Unsubscribed', 2027),
('Elijah',    'Jackson',   'elijah.jackson@husky.neu.edu',     '617-555-0120', 'Northeastern University', 'Subscribed',   2026),
('Amelia',    'White',     'amelia.white@husky.neu.edu',       '617-555-0121', 'Northeastern University', 'Subscribed',   2028),
('Lucas',     'Harris',    'lucas.harris@husky.neu.edu',       '617-555-0122', 'Northeastern University', 'Subscribed',   2025),
('Harper',    'Martin',    'harper.martin@husky.neu.edu',      '617-555-0123', 'Northeastern University', 'Unsubscribed', 2026),
('Mason',     'Cruz',      'mason.cruz@husky.neu.edu',         '617-555-0124', 'Northeastern University', 'Subscribed',   2027),
('Evelyn',    'Lopez',     'evelyn.lopez@husky.neu.edu',       '617-555-0125', 'Northeastern University', 'Subscribed',   2026),
('Logan',     'Robinson',  'logan.robinson@husky.neu.edu',     '617-555-0126', 'Northeastern University', 'Subscribed',   2025),
('Abigail',   'Walker',    'abigail.walker@husky.neu.edu',     '617-555-0127', 'Northeastern University', 'Unsubscribed', 2028),
('Jackson',   'Hall',      'jackson.hall@husky.neu.edu',       '617-555-0128', 'Northeastern University', 'Subscribed',   2026),
('Ella',      'Allen',     'ella.allen@husky.neu.edu',         '617-555-0129', 'Northeastern University', 'Subscribed',   2027),
('Aiden',     'Young',     'aiden.young@husky.neu.edu',        '617-555-0130', 'Northeastern University', 'Subscribed',   2025),
('Scarlett',  'Hernandez', 'scarlett.hernandez@husky.neu.edu', '617-555-0131', 'Northeastern University', 'Unsubscribed', 2026),
('Carter',    'King',      'carter.king@husky.neu.edu',        '617-555-0132', 'Northeastern University', 'Subscribed',   2028),
('Grace',     'Wright',    'grace.wright@husky.neu.edu',       '617-555-0133', 'Northeastern University', 'Subscribed',   2027),
('Sebastian', 'Scott',     'sebastian.scott@husky.neu.edu',    '617-555-0134', 'Northeastern University', 'Subscribed',   2026),
('Chloe',     'Torres',    'chloe.torres@husky.neu.edu',       '617-555-0135', 'Northeastern University', 'Unsubscribed', 2025);


INSERT INTO Venue (address, sport_type, capacity, name) VALUES
('346 Huntington Ave, Boston, MA 02115',  'Basketball',    200, 'Cabot Gym Court B'),
('150 Forsyth St, Boston, MA 02115',       'Volleyball',    80,  'Ell Hall Gym'),
('10 Coventry St, Boston, MA 02115',       'Soccer',        300, 'Kent Field'),
('100 Forsyth St, Boston, MA 02115',       'Tennis',        50,  'Forsyth Tennis Courts'),
('500 Huntington Ave, Boston, MA 02115',   'Badminton',     60,  'Marino Badminton Courts'),
('175 Hemenway St, Boston, MA 02115',      'Basketball',    120, 'Hemenway Gym'),
('55 Leon St, Boston, MA 02115',           'Volleyball',    90,  'Marino Rec Court B'),
('1 Forsyth St, Boston, MA 02115',         'Soccer',        180, 'West Village Field'),
('400 Huntington Ave, Boston, MA 02115',   'Flag Football', 250, 'Parsons Field South'),
('212 St. Botolph St, Boston, MA 02115',   'Basketball',    130, 'Cabot Gym Court C'),
('23 Leon St, Boston, MA 02115',           'Frisbee',       200, 'Centennial Common'),
('88 Forsyth St, Boston, MA 02115',        'Tennis',        45,  'Forsyth East Courts'),
('321 Huntington Ave, Boston, MA 02115',   'Volleyball',    75,  'Cabot Gym Volleyball Court'),
('77 St. Botolph St, Boston, MA 02115',    'Soccer',        220, 'Cabot Soccer Turf'),
('60 Leon St, Boston, MA 02115',           'Basketball',    110, 'Marino Gym B'),
('180 Hemenway St, Boston, MA 02115',      'Flag Football', 200, 'Hemenway Flag Field'),
('90 Coventry St, Boston, MA 02115',       'Badminton',     55,  'Coventry Sports Center'),
('33 St. Botolph St, Boston, MA 02115',    'Table Tennis',  40,  'Curry Student Center Game Room'),
('250 Huntington Ave, Boston, MA 02115',   'Frisbee',       300, 'Krentzman Quad'),
('45 Leon St, Boston, MA 02115',           'Soccer',        160, 'Marino Outdoor Field'),
('99 Forsyth St, Boston, MA 02115',        'Basketball',    100, 'Forsyth Gym'),
('200 St. Botolph St, Boston, MA 02115',   'Volleyball',    85,  'St. Botolph Recreation Center'),
('300 Hemenway St, Boston, MA 02115',      'Tennis',        60,  'Hemenway Tennis Courts'),
('66 Coventry St, Boston, MA 02115',       'Flag Football', 175, 'Coventry Flag Field'),
('11 Leon St, Boston, MA 02115',           'Frisbee',       220, 'Leon Street Quad'),
('150 Huntington Ave, Boston, MA 02115',   'Basketball',    140, 'Huntington Gym'),
('44 St. Botolph St, Boston, MA 02115',    'Soccer',        190, 'Botolph Soccer Field');
