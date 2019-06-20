-- Initialize the database.

CREATE TABLE IF NOT EXISTS `users` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_name` char(16) NOT NULL,
  `password` varchar(128) NOT NULL,
  `user_type` tinyint(3) unsigned NOT NULL DEFAULT 0 COMMENT '用户类型，1超级用户，0普通用户',
  `avatar_name` varchar(256) NOT NULL DEFAULT 'null.jpg' COMMENT '头像名',
  `last_login_time` datetime DEFAULT NULL COMMENT '用户最后登录时间',
  `comment` varchar(100) DEFAULT NULL COMMENT '备注',
  `login_count` int(10) unsigned NOT NULL DEFAULT 0 COMMENT '登录次数',
  `user_status` tinyint(3) unsigned NOT NULL DEFAULT 1 COMMENT '是否允许登录，1 允许',
  `create_time` datetime NOT NULL DEFAULT curtime() COMMENT '创建时间',
  PRIMARY KEY (`id`),
  UNIQUE KEY `users_user_name_IDX` (`user_name`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=2 DEFAULT CHARSET=utf8;

CREATE TABLE IF NOT EXISTS `yutong_vehicle1` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `province` varchar(100) DEFAULT NULL COMMENT '省',
  `city` varchar(100) DEFAULT NULL COMMENT '市',
  `timestamp` datetime DEFAULT NULL COMMENT 'CST 时间',
  `bty_t_vol` decimal(10,2) DEFAULT NULL COMMENT '电池总电压',
  `bty_t_curr` decimal(10,2) DEFAULT NULL COMMENT '电池总电流',
  `battery_soc` decimal(5,2) DEFAULT NULL COMMENT 'soc',
  `s_b_max_t` int(11) DEFAULT NULL COMMENT '电池最高温度',
  `max_t_s_b_num` int(11) DEFAULT NULL COMMENT '最高温度电池号',
  `s_b_min_t` int(11) DEFAULT NULL COMMENT '电池最低温度',
  `min_t_s_b_num` int(11) DEFAULT NULL COMMENT '最低温度电池号',
  `s_b_max_v` decimal(10,6) DEFAULT NULL COMMENT '电池最高电压',
  `max_v_e_core_num` int(11) DEFAULT NULL COMMENT '最高电压电芯号',
  `s_b_min_v` decimal(10,6) DEFAULT NULL COMMENT '电池最低电压',
  `min_v_e_core_num` int(11) DEFAULT NULL COMMENT '最低电压电芯号',
  `p_t_p` decimal(10,2) DEFAULT NULL COMMENT '正向累计电量',
  `r_t_p` decimal(10,2) DEFAULT NULL COMMENT '反向累计电量',
  `total_mileage` int(11) DEFAULT NULL COMMENT '总里程',
  `bty_sys_rated_capacity` int(11) DEFAULT NULL COMMENT '额定容量',
  `bty_sys_rated_consumption` int(11) DEFAULT NULL COMMENT '额定能量',
  `met_spd` int(11) DEFAULT NULL COMMENT '车速',
  `byt_ma_sys_state` int(11) DEFAULT NULL COMMENT '未知',
  PRIMARY KEY (`id`),
  KEY `vehicle1_timestamp_IDX` (`timestamp`) USING BTREE
) ENGINE=InnoDB AUTO_INCREMENT=167719 DEFAULT CHARSET=utf8 COMMENT='vehicle_id: 4F37195C1A908CFBE0532932A8C0EECB';