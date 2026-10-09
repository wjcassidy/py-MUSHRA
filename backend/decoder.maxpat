{
	"patcher" : 	{
		"fileversion" : 1,
		"appversion" : 		{
			"major" : 8,
			"minor" : 6,
			"revision" : 5,
			"architecture" : "x64",
			"modernui" : 1
		}
,
		"classnamespace" : "box",
		"rect" : [ 289.0, 116.0, 640.0, 480.0 ],
		"bglocked" : 0,
		"openinpresentation" : 0,
		"default_fontsize" : 12.0,
		"default_fontface" : 0,
		"default_fontname" : "Arial",
		"gridonopen" : 1,
		"gridsize" : [ 15.0, 15.0 ],
		"gridsnaponopen" : 1,
		"objectsnaponopen" : 1,
		"statusbarvisible" : 2,
		"toolbarvisible" : 1,
		"lefttoolbarpinned" : 0,
		"toptoolbarpinned" : 0,
		"righttoolbarpinned" : 0,
		"bottomtoolbarpinned" : 0,
		"toolbars_unpinned_last_save" : 0,
		"tallnewobj" : 0,
		"boxanimatetime" : 200,
		"enablehscroll" : 1,
		"enablevscroll" : 1,
		"devicewidth" : 0.0,
		"description" : "",
		"digest" : "",
		"tags" : "",
		"style" : "",
		"subpatcher_template" : "",
		"assistshowspatchername" : 0,
		"boxes" : [ 			{
				"box" : 				{
					"id" : "obj-6",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 345.5, 321.0, 276.5, 202.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-5",
					"maxclass" : "meter~",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "float" ],
					"patching_rect" : [ 345.0, 171.0, 277.0, 134.0 ]
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-4",
					"linecount" : 2,
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 0,
					"patching_rect" : [ 139.0, 283.0, 530.0, 35.0 ],
					"text" : "mc.dac~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40 41 42 43 44 45 46 47 48"
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"enablehscroll" : 0,
					"enablevscroll" : 0,
					"id" : "obj-3",
					"lockeddragscroll" : 0,
					"lockedsize" : 0,
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 7,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "multichannelsignal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 139.0, 209.0, 168.0, 22.0 ],
					"save" : [ "#N", "mcs.vst~", "loaduniqueid", 0, 25, 48, "AllRADecoder", ";" ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_invisible" : 1,
							"parameter_longname" : "mcs.vst~[1]",
							"parameter_modmode" : 0,
							"parameter_shortname" : "mcs.vst~[1]",
							"parameter_type" : 3
						}

					}
,
					"saved_object_attributes" : 					{
						"parameter_enable" : 1,
						"parameter_mappable" : 0
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "mcs.vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{
							"pluginname" : "AllRADecoder.vstinfo",
							"plugindisplayname" : "AllRADecoder",
							"pluginsavedname" : "",
							"pluginsaveduniqueid" : 0,
							"version" : 1,
							"isbank" : 0,
							"isbase64" : 1,
							"blob" : "4531.CMlaKA....fQPMDZ....ADDaREF..j.A....BPVYlEVcrQG..............................DwcVMjLg3VD...O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOAwFaREDQkM1ajUlb9vCTAIUPMARZj0iHjU1XuQVYx8jbjUlbh.hcgwVck0iHy3BLh7hO7.UPRETSfjFY8HRY3A2axQGQkM1ajUlbh.hcgwVck0iHw3BLh7hO7.UPRETSfjFY8HRY3A2axQGSgk2a0QmHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhjlavUGcOIGYkI2TkQGco41Yh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HRcyU1TNMCQh.hcgwVck0iHw3BLh7hO7.UPRETSfjFY8Hxckk1YnQ2bh.hcgwVck0iHv3BLh7hO77zTCMzatYVZmAhTkMVYoYWYxA0axQWOhzRLh.xTk4FYkIWRP0iHh.xTk4FYkIGTuIGc8HRKwHBHSUlajUlbOM0PAQFYxU1by0iHuDDarIUPDU1XuQVYx8hHfLUYtQVYxkjazUlb1EFa8HRLv.iHu3COL8VcjMGbkE1ZkI2b9vSQrUVak4FcfDjdo0VczgVOh.iKvHBHEwVY1EFco8la8HRNv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HBLt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iH2HiKvHBHEwVY1EFco8la8HhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHzHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iH0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwPCMt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhXiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhbiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHv3BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRNh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhLiMt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDCLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDSLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhDCL33BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRLxHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRLzHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwPCMt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDSMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRLvfiKvHBHEwVY1EFco8la8HxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwXiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDyMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzxL13BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRL3HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HBLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHx.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHy.iKvHBHEwVY1EFco8la8HBLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HhLwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HhMv3BLh.RQrUlcgQWZu4VOh.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhHiLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhjCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHwHCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxPiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHwTCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxTiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOh.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhHiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRL0.iKvHBHEwVY1EFco8la8HBLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HhL2HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwHCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsjCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxjiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsXCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHy.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsLCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyDiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHv3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHyXiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLCMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHsLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HxL0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLvfiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhDCMz3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHybiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCMz3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyjiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCL33BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHz.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iHsLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HBMwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKyXiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPiLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOh.iKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPCMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHsXCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HBM0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRLzPiKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPyMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzxMx3BLh.RQrUlcgQWZu4VOhzhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHzfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO77BSuUGYyAWYgsVYxMmO77RPrwlTAQTYi8FYkImO.."
						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "AllRADecoder",
									"origin" : "AllRADecoder.vstinfo",
									"type" : "VST",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{
										"pluginname" : "AllRADecoder.vstinfo",
										"plugindisplayname" : "AllRADecoder",
										"pluginsavedname" : "",
										"pluginsaveduniqueid" : 0,
										"version" : 1,
										"isbank" : 0,
										"isbase64" : 1,
										"blob" : "4531.CMlaKA....fQPMDZ....ADDaREF..j.A....BPVYlEVcrQG..............................DwcVMjLg3VD...O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOAwFaREDQkM1ajUlb9vCTAIUPMARZj0iHjU1XuQVYx8jbjUlbh.hcgwVck0iHy3BLh7hO7.UPRETSfjFY8HRY3A2axQGQkM1ajUlbh.hcgwVck0iHw3BLh7hO7.UPRETSfjFY8HRY3A2axQGSgk2a0QmHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhjlavUGcOIGYkI2TkQGco41Yh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HRcyU1TNMCQh.hcgwVck0iHw3BLh7hO7.UPRETSfjFY8Hxckk1YnQ2bh.hcgwVck0iHv3BLh7hO77zTCMzatYVZmAhTkMVYoYWYxA0axQWOhzRLh.xTk4FYkIWRP0iHh.xTk4FYkIGTuIGc8HRKwHBHSUlajUlbOM0PAQFYxU1by0iHuDDarIUPDU1XuQVYx8hHfLUYtQVYxkjazUlb1EFa8HRLv.iHu3COL8VcjMGbkE1ZkI2b9vSQrUVak4FcfDjdo0VczgVOh.iKvHBHEwVY1EFco8la8HRNv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HBLt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iH2HiKvHBHEwVY1EFco8la8HhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHzHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iH0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwPCMt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhXiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iH1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhbiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHv3BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRNh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhLiMt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDCLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDSLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhDCL33BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRLxHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRLzHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwPCMt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDSMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRLvfiKvHBHEwVY1EFco8la8HxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHwXiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iHy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhDyMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzxL13BLh.RQrUlcgQWZu4VOhLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HRL3HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HBLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHx.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHy.iKvHBHEwVY1EFco8la8HBLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HhLwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HhMv3BLh.RQrUlcgQWZu4VOh.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhHiLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhjCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHwHCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxPiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHwTCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxTiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOh.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhHiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRL0.iKvHBHEwVY1EFco8la8HBLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HhL2HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKwHCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsjCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHxjiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsXCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHy.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsLCLt.iHfTDakYWXzk1at0iHv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyDiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHv3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyLiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHyXiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLCMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHsLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HxL0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLvfiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhLiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhDCMz3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHybiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCNv3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCMz3BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHyjiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsDCL33BLh.RQrUlcgQWZu4VOhzxLv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHz.iHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO7TDak0VYtQGHAoWZsUGcn0iHsbiLt.iHfTDakYWXzk1at0iHsLCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HBMwHBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRKyXiKvHBHEwVY1EFco8la8HRKy.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPiLh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOh.iKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPCMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhbiLt.iHfTDakYWXzk1at0iHsXCLt.iHfHUXjkVcy0iHw3BLh.xPnElatUFa8HBM0HBHI0VXmklagIWd8HBLh.xQgkla8HRLt.iHu3COEwVYsUlazARP5kVa0QGZ8HRLzPiKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPiMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzRLzPiKvHBHEwVY1EFco8la8HRK1.iKvHBHREFYoU2b8HRLt.iHfLDZg4lakwVOhPyMh.RRsE1Yo4VXxkWOh.iHfbTXo4VOhDiKvHxK9vSQrUVak4FcfDjdo0VczgVOhzxMx3BLh.RQrUlcgQWZu4VOhzhMv3BLh.hTgQVZ0MWOhDiKvHBHCgVXt4VYr0iHzfiHfjTagcVZtElb40iHvHBHGEVZt0iHw3BLh7hO77BSuUGYyAWYgsVYxMmO77RPrwlTAQTYi8FYkImO.."
									}
,
									"fileref" : 									{
										"name" : "AllRADecoder",
										"filename" : "AllRADecoder.maxsnap",
										"filepath" : "~/Documents/Max 8/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "a91733ba3712a09781aea2069c48e3c0"
									}

								}
, 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "AllRADecoder",
									"origin" : "AllRADecoder.vstinfo",
									"type" : "VST",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"fileref" : 									{
										"name" : "AllRADecoder",
										"filename" : "AllRADecoder.maxsnap",
										"filepath" : "~/Documents/PhD/AmbiMuS-RealWorldVal/AmbiMuS-RealWorldVal/data",
										"filepos" : -1,
										"snapshotfileid" : "0a8e5f4491c16f6008f98ec8d1abcc69"
									}

								}
, 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "AllRADecoder",
									"origin" : "AllRADecoder.vstinfo",
									"type" : "VST",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"fileref" : 									{
										"name" : "AllRADecoder",
										"filename" : "AllRADecoder_20250513.maxsnap",
										"filepath" : "~/Documents/PhD/AmbiMuS-RealWorldVal/AmbiMuS-RealWorldVal/data",
										"filepos" : -1,
										"snapshotfileid" : "897a941e0cc1c4dc5e7a9a08974ff727"
									}

								}
 ]
						}

					}
,
					"text" : "mcs.vst~ 25 48 AllRADecoder",
					"varname" : "mcs.vst~[1]",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"autosave" : 1,
					"bgmode" : 0,
					"border" : 0,
					"clickthrough" : 0,
					"enablehscroll" : 0,
					"enablevscroll" : 0,
					"id" : "obj-2",
					"lockeddragscroll" : 0,
					"lockedsize" : 0,
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 7,
					"offset" : [ 0.0, 0.0 ],
					"outlettype" : [ "multichannelsignal", "", "list", "int", "", "", "" ],
					"patching_rect" : [ 139.0, 178.0, 166.0, 22.0 ],
					"save" : [ "#N", "mcs.vst~", "loaduniqueid", 0, 25, 25, "SceneRotator", ";" ],
					"saved_attribute_attributes" : 					{
						"valueof" : 						{
							"parameter_invisible" : 1,
							"parameter_longname" : "mcs.vst~",
							"parameter_modmode" : 0,
							"parameter_shortname" : "mcs.vst~",
							"parameter_type" : 3
						}

					}
,
					"saved_object_attributes" : 					{
						"parameter_enable" : 1,
						"parameter_mappable" : 0
					}
,
					"snapshot" : 					{
						"filetype" : "C74Snapshot",
						"version" : 2,
						"minorversion" : 0,
						"name" : "snapshotlist",
						"origin" : "mcs.vst~",
						"type" : "list",
						"subtype" : "Undefined",
						"embed" : 1,
						"snapshot" : 						{
							"pluginname" : "SceneRotator.vstinfo",
							"plugindisplayname" : "SceneRotator",
							"pluginsavedname" : "",
							"pluginsaveduniqueid" : 0,
							"version" : 1,
							"isbank" : 0,
							"isbase64" : 1,
							"blob" : "798.CMlaKA....fQPMDZ....AL0XR8F..PfA....A........................................Hf3VMjLgjs....O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOSMVYtUlTuQWXz8lbfzTZjkFQkYWZiUlSg0VY8HhHfzTZjkFQkYWZiU1TigVYsUVOh.iH9vCTAIUPMARZj0iHo4lckIGcPkFciglHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzEUcgQWYx4VZu4lHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzI0arwlHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzkUX2IBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHuIGYkI2TkQGco41Yh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HBboQ2XnIBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHwcmHfXWXrUWY8HBLtfCL3.CLv.CN2byL3.yL2DiHu3COPEjTA0DHoQVOhDGdh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HRb4IBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHwomHfXWXrUWY8HBLtTCN4.CLvDCL0fSM2fCM4DiHu3COPEjTA0DHoQVOhH2arwlHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhH2azEFco8laSUVb0UlaiUlHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhT2bkMkSyPjHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhjWX2IBH1EFa0UVOhbiLtDiM4jSN3DiM3jCM0LSLh7hO77zTCMzatYVZmAhTkMVYoYWYxA0axQWOhzRLh.xTk4FYkIWRP0iHh.xTk4FYkIGTuIGc8HRKwHBHSUlajUlbOM0PAQFYxU1by0iHuL0Xk4VYR8FcgQ2ax8hHfLUYtQVYxkjazUlb1EFa8HRLv.iHu3COuL0Xk4VYR8FcgQ2ax4C."
						}
,
						"snapshotlist" : 						{
							"current_snapshot" : 0,
							"entries" : [ 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "SceneRotator",
									"origin" : "SceneRotator.vstinfo",
									"type" : "VST",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"snapshot" : 									{
										"pluginname" : "SceneRotator.vstinfo",
										"plugindisplayname" : "SceneRotator",
										"pluginsavedname" : "",
										"pluginsaveduniqueid" : 0,
										"version" : 1,
										"isbank" : 0,
										"isbase64" : 1,
										"blob" : "798.CMlaKA....fQPMDZ....AL0XR8F..PfA....A........................................Hf3VMjLgjs....O+fWarAhckI2bo8la8HRLt.iHfTlai8FYo41Y8HRUTYTK3HxO9.BOSMVYtUlTuQWXz8lbfzTZjkFQkYWZiUlSg0VY8HhHfzTZjkFQkYWZiU1TigVYsUVOh.iH9vCTAIUPMARZj0iHo4lckIGcPkFciglHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzEUcgQWYx4VZu4lHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzI0arwlHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhjla1UlbzkUX2IBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHuIGYkI2TkQGco41Yh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HBboQ2XnIBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHwcmHfXWXrUWY8HBLtfCL3.CLv.CN2byL3.yL2DiHu3COPEjTA0DHoQVOhDGdh.hcgwVck0iHv3BLh7hO7.UPRETSfjFY8HRb4IBH1EFa0UVOh.iKvHxK9vCTAIUPMARZj0iHwomHfXWXrUWY8HBLtTCN4.CLvDCL0fSM2fCM4DiHu3COPEjTA0DHoQVOhH2arwlHfXWXrUWY8HBLt.iHu3COPEjTA0DHoQVOhH2azEFco8laSUVb0UlaiUlHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhT2bkMkSyPjHfXWXrUWY8HRLt.iHu3COPEjTA0DHoQVOhjWX2IBH1EFa0UVOhbiLtDiM4jSN3DiM3jCM0LSLh7hO77zTCMzatYVZmAhTkMVYoYWYxA0axQWOhzRLh.xTk4FYkIWRP0iHh.xTk4FYkIGTuIGc8HRKwHBHSUlajUlbOM0PAQFYxU1by0iHuL0Xk4VYR8FcgQ2ax8hHfLUYtQVYxkjazUlb1EFa8HRLv.iHu3COuL0Xk4VYR8FcgQ2ax4C."
									}
,
									"fileref" : 									{
										"name" : "SceneRotator",
										"filename" : "SceneRotator.maxsnap",
										"filepath" : "~/Documents/Max 8/Snapshots",
										"filepos" : -1,
										"snapshotfileid" : "85d96c4010ce31ead563895492509a2b"
									}

								}
, 								{
									"filetype" : "C74Snapshot",
									"version" : 2,
									"minorversion" : 0,
									"name" : "SceneRotator",
									"origin" : "SceneRotator.vstinfo",
									"type" : "VST",
									"subtype" : "AudioEffect",
									"embed" : 0,
									"fileref" : 									{
										"name" : "SceneRotator",
										"filename" : "SceneRotator.maxsnap",
										"filepath" : "~/Documents/PhD/AmbiMuS-RealWorldVal/AmbiMuS-RealWorldVal/data",
										"filepos" : -1,
										"snapshotfileid" : "c78c4d1f22926632c3e57a2cf20b65ad"
									}

								}
 ]
						}

					}
,
					"text" : "mcs.vst~ 25 25 SceneRotator",
					"varname" : "mcs.vst~",
					"viewvisibility" : 0
				}

			}
, 			{
				"box" : 				{
					"id" : "obj-1",
					"maxclass" : "newobj",
					"numinlets" : 1,
					"numoutlets" : 1,
					"outlettype" : [ "multichannelsignal" ],
					"patching_rect" : [ 139.0, 124.0, 410.0, 22.0 ],
					"text" : "mc.adc~ 1 2 3 4 5 6 7 8 9 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25"
				}

			}
 ],
		"lines" : [ 			{
				"patchline" : 				{
					"destination" : [ "obj-2", 0 ],
					"order" : 1,
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-5", 0 ],
					"order" : 0,
					"source" : [ "obj-1", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-3", 0 ],
					"source" : [ "obj-2", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-4", 0 ],
					"order" : 1,
					"source" : [ "obj-3", 0 ]
				}

			}
, 			{
				"patchline" : 				{
					"destination" : [ "obj-6", 0 ],
					"order" : 0,
					"source" : [ "obj-3", 0 ]
				}

			}
 ],
		"parameters" : 		{
			"obj-2" : [ "mcs.vst~", "mcs.vst~", 0 ],
			"obj-3" : [ "mcs.vst~[1]", "mcs.vst~[1]", 0 ],
			"parameterbanks" : 			{
				"0" : 				{
					"index" : 0,
					"name" : "",
					"parameters" : [ "-", "-", "-", "-", "-", "-", "-", "-" ]
				}

			}
,
			"inherited_shortname" : 1
		}
,
		"dependency_cache" : [ 			{
				"name" : "AllRADecoder.maxsnap",
				"bootpath" : "~/Documents/Max 8/Snapshots",
				"patcherrelativepath" : "../../../../Documents/Max 8/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "AllRADecoder_20250513.maxsnap",
				"bootpath" : "~/Documents/PhD/AmbiMuS-RealWorldVal/AmbiMuS-RealWorldVal/data",
				"patcherrelativepath" : "../../../../Documents/PhD/AmbiMuS-RealWorldVal/AmbiMuS-RealWorldVal/data",
				"type" : "mx@s",
				"implicit" : 1
			}
, 			{
				"name" : "SceneRotator.maxsnap",
				"bootpath" : "~/Documents/Max 8/Snapshots",
				"patcherrelativepath" : "../../../../Documents/Max 8/Snapshots",
				"type" : "mx@s",
				"implicit" : 1
			}
 ],
		"autosave" : 0
	}

}
