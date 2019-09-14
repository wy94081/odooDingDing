# -*- coding: utf-8 -*-
###################################################################################
# Copyright (C) 2019 SuXueFeng
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
###################################################################################
import calendar
import time
import logging
from datetime import date, datetime, timedelta

from odoo import api, fields, models
from odoo.exceptions import UserError

_logger = logging.getLogger(__name__)


class WageEmpAttendanceAnnal(models.TransientModel):
    _description = '计算考勤结果'
    _name = 'wage.employee.attendance.annal.transient'

    SourceType = [
        ('dingding', '钉钉考勤结果'),
        ('odoo', 'Odoo出勤记录'),
        ('and', '两者同时获取')
    ]

    soure_type = fields.Selection(string=u'考勤结果来源', selection=SourceType, default='odoo', required=True)
    start_date = fields.Datetime(string=u'考勤开始日期', required=True)
    end_date = fields.Datetime(string=u'考勤结束日期', required=True)
    emp_ids = fields.Many2many(comodel_name='hr.employee', relation='attendance_total_and_hr_employee_rel',
                               column1='attendance_id', column2='emp_id', string=u'员工', required=True)
    is_all_emp = fields.Boolean(string=u'全部员工')

    @api.onchange('is_all_emp')
    def onchange_all_emp(self):
        if self.is_all_emp:
            emps = self.env['hr.employee'].search([('ding_id', '!=', '')])
            if len(emps) <= 0:
                raise UserError("员工钉钉Id不存在！也许是你的员工未同步导致的！")
            self.emp_ids = [(6, 0, emps.ids)]

    # @api.onchange('start_date')
    # def _compute_end_date(self):
    #     for rec in self:
    #         if rec.start_date:
    #             firstDay, lastDay = self.getMonthFirstDayAndLastDay(year=rec.start_date.year, month=rec.start_date.month)
    #             rec.end_date = lastDay

    @api.model
    def getMonthFirstDayAndLastDay(self, year=None, month=None):
        """
        :param year: 年份，默认是本年，可传int或str类型
        :param month: 月份，默认是本月，可传int或str类型
        :return: firstDay: 当月的第一天，datetime.date类型
                  lastDay: 当月的最后一天，datetime.date类型
        """
        if year:
            year = int(year)
        else:
            year = fields.Date.today().year

        if month:
            month = int(month)
        else:
            month = fields.Date.today().month

        # 获取当月第一天的星期和当月的总天数
        firstDayWeekDay, monthRange = calendar.monthrange(year, month)

        # 获取当月的第一天
        firstDay = date(year=year, month=month, day=1)
        lastDay = date(year=year, month=month, day=monthRange)

        return firstDay, lastDay

    @api.multi
    def compute_attendance_result(self):
        """
        立即计算考勤结果
        :return:
        """
        self.attendance_total_cal(self.emp_ids, self.start_date, self.end_date)

        # 计算后重载考勤统计列表
        action = self.env.ref('odoo_wage_manage.wage_employee_attendance_annal_action')
        action_dict = action.read()[0]
        return action_dict

    def date_range(self, start_date, end_date):
        """
        生成一个 起始时间 到 结束时间 的一个列表
        TODO 起始时间和结束时间相差过大时，考虑使用 yield
        :param start_date:
        :param end_date:
        :return:
        """
        date_tmp = [start_date, ]
        # print(date_tmp[-1])
        while date_tmp[-1] < end_date:
            date_tmp.append(date_tmp[-1] + timedelta(days=1))
        return date_tmp

    @api.multi
    def attendance_cal(self, emp_list, start_date, end_date):
        """
        生成考勤日报表
        """
        # 获取排班信息 get_scheduling_info_dict
        # 获取班次信息 get_shift_info_dict
        # 获取签卡数据 get_edit_attendance_dict
        # 获取请假拆分后的数据 get_leave_detail_dict
        # TODO 获取出差数据
        # 获取原始打卡数据 get_original_card_dict
        # 数据整合 数据结构
        # 数据写入
        # 获取班次信息 get_shift_info_dict
        # shift_info_dict = get_shift_info_dict()
        # 考勤数据列表
        # attendance_info_list = []

        for emp in emp_list:
            # 删除已存在的
            start_datetime = datetime(start_date.year, start_date.month, start_date.day)
            end_datetime = datetime(end_date.year, end_date.month, end_date.day)
            old_attendance_info = self.env['attendance.info'].sudo().search(
                [('employee_id', '=', emp.id), ('workDate', '>=', start_datetime), ('workDate', '<=', end_datetime)])
            if old_attendance_info:
                old_attendance_info.sudo().unlink()
            # # 获取排班信息 get_scheduling_info_dict
            # scheduling_info_dict = get_scheduling_info_dict(emp, start_date, end_date)
            # # 获取签卡数据 get_edit_attendance_dict
            # edit_attendance_dict = get_edit_attendance_dict(emp, start_date, end_date)
            # 获取请假拆分后的数据 get_leave_detail_dict
            # leave_detail_dict = get_leave_detail_dict(emp, start_date, end_date)
            # 获取原始打卡数据 get_original_card_dict
            # original_card_dict = self.get_original_card_dict(emp, start_date, end_date)
            # 整合打卡、签卡、请假数据，赋值
            # print(scheduling_info_dict, edit_attendance_dict, leave_detail_dict, original_card_dict)
            # date_list = self.date_range(start_date, end_date)
            # for work_date in date_list:
            # work_datetime = datetime(work_date.year, work_date.month, work_date.day)
            work_date_attendance_result = self.env['hr.attendance.result'].sudo().search(
                [('emp_id', '=', emp.id), ('work_date', '>=', start_datetime), ('work_date', '<=', end_datetime)])
            # work_date_attendance_result = self.env['hr.attendance.result'].sudo().search(
            #     [('emp_id', '=', emp.id), ('work_date', '=', work_datetime)])
            OnDuty_list = list()
            OffDuty_list = list()
            for rec in work_date_attendance_result:
                data = {
                    'employee_id': emp.id,
                    'workDate': rec.work_date,  # 工作日
                    'ding_group_id': rec.ding_group_id.id,
                    'attendance_date_status': '00',
                }
                # 判断是否周末加班
                if datetime.isoweekday(rec.work_date) in (6, 7):
                    data.update({'attendance_date_status': '01'})
                # 判断是否节假日加班
                elif self.env['legal.holiday'].sudo().search([('legal_holiday', '=', rec.work_date.date())]):
                    data.update({'attendance_date_status': '02'})
                if rec.check_type == 'OnDuty':
                    data.update({
                        'check_in': rec.check_in,
                        'on_planId': rec.plan_id.plan_id,
                        'on_timeResult': rec.timeResult,
                        'on_baseCheckTime': rec.baseCheckTime,
                        'on_sourceType': rec.sourceType,
                        'on_procInstId': rec.procInstId
                    })
                    OnDuty_list.append(data)
                elif rec.check_type == 'OffDuty':
                    data.update({
                        'check_out': rec.check_in,
                        'off_planId': rec.plan_id.plan_id,
                        'off_timeResult': rec.timeResult,
                        'off_baseCheckTime': rec.baseCheckTime,
                        'off_sourceType': rec.sourceType,
                        'off_procInstId': rec.procInstId
                    })
                    OffDuty_list.append(data)
            # 上班考勤结果列表与下班考勤结果列表按时间排序后合并
            OnDuty_list.sort(key=lambda x: x['check_in'])
            # logging.info(">>>获取OnDuty_list结果%s", OnDuty_list)
            OffDuty_list.sort(key=lambda x: x['check_out'])
            # logging.info(">>>获取OffDuty_list结果%s", OffDuty_list)
            duty_list = list()
            on_planId_list = list()
            for onduty in OnDuty_list:
                for offduty in OffDuty_list:
                    datetime_check_out = offduty.get('check_out')
                    datetime_check_in = onduty.get('check_in')
                    if int(offduty.get('off_planId')) == int(onduty.get('on_planId')) + 1 and \
                            offduty.get('workDate') == onduty.get('workDate'):
                        duty_tmp = dict(onduty, **offduty)
                        duty_list.append(duty_tmp)
                        on_planId_list.append(onduty.get('on_planId'))
                    elif datetime_check_out > datetime_check_in and \
                            offduty.get('workDate') == onduty.get('workDate') and \
                            onduty.get('on_planId') not in on_planId_list:
                        duty_tmp = dict(onduty, **offduty)
                        duty_list.append(duty_tmp)
                        on_planId_list.append(onduty.get('on_planId'))
            # 剩余还未匹配到下班记录的考勤（如当天）
            for onduty in OnDuty_list:
                if onduty.get('on_planId') not in on_planId_list:
                    duty_list.append(onduty)
            # 将合并的考勤导入odoo考勤
            duty_list.sort(key=lambda x: x['check_in'])
            logging.info(">>>获取duty_list结果%s", duty_list)
            # 判断是否在请假期间
            # TODO 班次时间段内请假未考虑
            # duty_info = []
            # for duty in duty_list:
            #     leave_info = self.env['hr.leaves.list'].sudo().search([('user_id', '=', emp.id), ('start_time', '<=', work_datetime), ('end_time', '>=', work_datetime)])
            #     if len(leave_info) > 0:
            #         delta = duty['off_baseCheckTime'] - duty['on_baseCheckTime']
            #         leave_hours = delta.total_seconds() / 3600.0
            #         duty.update({'leave_hours': leave_hours})
            #     duty_info.append(duty)

            self.env['attendance.info'].sudo().create(duty_list)

    @api.multi
    def attendance_cal_v2(self, emp_list, start_date, end_date):
        """
        生成考勤日报表
        """
        # 获取排班信息 get_scheduling_info_dict
        # 获取班次信息 get_shift_info_dict
        # 获取签卡数据 get_edit_attendance_dict
        # 获取请假拆分后的数据 get_leave_detail_dict
        # TODO 获取出差数据
        # 获取原始打卡数据 get_original_card_dict
        # 数据整合 数据结构
        # 数据写入
        # 获取班次信息 get_shift_info_dict
        # shift_info_dict = get_shift_info_dict()
        # 考勤数据列表
        # attendance_info_list = []

        for emp in emp_list:
            # 删除已存在的
            start_datetime = datetime(start_date.year, start_date.month, start_date.day)
            end_datetime = datetime(end_date.year, end_date.month, end_date.day)
            old_attendance_info = self.env['attendance.info'].sudo().search(
                [('employee_id', '=', emp.id), ('workDate', '>=', start_datetime), ('workDate', '<=', end_datetime)])
            if old_attendance_info:
                old_attendance_info.sudo().unlink()
            # # 获取排班信息 get_scheduling_info_dict
            # scheduling_info_dict = get_scheduling_info_dict(emp, start_date, end_date)
            # # 获取签卡数据 get_edit_attendance_dict
            # edit_attendance_dict = get_edit_attendance_dict(emp, start_date, end_date)
            # 获取请假拆分后的数据 get_leave_detail_dict
            # leave_detail_dict = get_leave_detail_dict(emp, start_date, end_date)
            # 获取原始打卡数据 get_original_card_dict
            # original_card_dict = self.get_original_card_dict(emp, start_date, end_date)
            # 整合打卡、签卡、请假数据，赋值
            # print(scheduling_info_dict, edit_attendance_dict, leave_detail_dict, original_card_dict)
            date_list = self.date_range(start_date, end_date)
            for work_date in date_list:
                work_datetime = datetime(work_date.year, work_date.month, work_date.day)
                # work_date_attendance_result = self.env['hr.attendance.result'].sudo().search(
                #     [('emp_id', '=', emp.id), ('check_in', '>=', start_date), ('check_in', '<=', end_date)])
                work_date_attendance_result = self.env['hr.attendance.result'].sudo().search(
                    [('emp_id', '=', emp.id), ('work_date', '=', work_datetime)])
                OnDuty_list = list()
                OffDuty_list = list()
                for rec in work_date_attendance_result:
                    print('11111111111111111',work_datetime)
                    print('22222222222222222',rec.work_date)
                    data = {
                        'employee_id': emp.id,
                        'workDate': rec.work_date,  # 工作日
                        'ding_group_id': rec.ding_group_id.id,
                        'attendance_date_status': '00',
                    }
                    # 判断是否周末加班
                    if datetime.isoweekday(rec.work_date) in (6, 7):
                        data.update({'attendance_date_status': '01'})
                    # 判断是否节假日加班
                    elif self.env['legal.holiday'].sudo().search([('legal_holiday', '=', rec.work_date.date())]):
                        data.update({'attendance_date_status': '02'})
                    if rec.check_type == 'OnDuty':
                        data.update({
                            'check_in': rec.check_in,
                            'on_planId': rec.plan_id.plan_id,
                            'on_timeResult': rec.timeResult,
                            'on_baseCheckTime': rec.baseCheckTime,
                            'on_sourceType': rec.sourceType,
                            'on_procInstId': rec.procInstId
                        })
                        OnDuty_list.append(data)
                    elif rec.check_type == 'OffDuty':
                        data.update({
                            'check_out': rec.check_in,
                            'off_planId': rec.plan_id.plan_id,
                            'off_timeResult': rec.timeResult,
                            'off_baseCheckTime': rec.baseCheckTime,
                            'off_sourceType': rec.sourceType,
                            'off_procInstId': rec.procInstId
                        })
                        OffDuty_list.append(data)
                # 上班考勤结果列表与下班考勤结果列表按时间排序后合并
                OnDuty_list.sort(key=lambda x: x['check_in'])
                # logging.info(">>>获取OnDuty_list结果%s", OnDuty_list)
                OffDuty_list.sort(key=lambda x: x['check_out'])
                # logging.info(">>>获取OffDuty_list结果%s", OffDuty_list)
                duty_list = list()
                on_planId_list = list()
                for onduty in OnDuty_list:
                    for offduty in OffDuty_list:
                        datetime_check_out = offduty.get('check_out')
                        datetime_check_in = onduty.get('check_in')
                        if int(offduty.get('off_planId')) == int(onduty.get('on_planId')) + 1 and \
                                offduty.get('workDate') == onduty.get('workDate'):
                            duty_tmp = dict(onduty, **offduty)
                            duty_list.append(duty_tmp)
                            on_planId_list.append(onduty.get('on_planId'))
                        elif datetime_check_out > datetime_check_in and \
                                offduty.get('workDate') == onduty.get('workDate') and \
                                onduty.get('on_planId') not in on_planId_list:
                            duty_tmp = dict(onduty, **offduty)
                            duty_list.append(duty_tmp)
                            on_planId_list.append(onduty.get('on_planId'))
                # 剩余还未匹配到下班记录的考勤（如当天）
                for onduty in OnDuty_list:
                    if onduty.get('on_planId') not in on_planId_list:
                        duty_list.append(onduty)
                # 将合并的考勤导入odoo考勤
                duty_list.sort(key=lambda x: x['workDate'])
                logging.info(">>>获取duty_list结果%s", duty_list)
                # 判断是否在请假期间
                # TODO 班次时间段内请假未考虑
                duty_info = []
                for duty in duty_list:
                    leave_info = self.env['hr.leaves.list'].sudo().search([('user_id', '=', emp.id), ('start_time', '<=', work_datetime), ('end_time', '>=', work_datetime)])
                    if len(leave_info) > 0:
                        delta = duty['off_baseCheckTime'] - duty['on_baseCheckTime']
                        leave_hours = delta.total_seconds() / 3600.0
                        duty.update({'leave_hours': leave_hours})
                    duty_info.append(duty)

                self.env['attendance.info'].sudo().create(duty_info)

            # 检索请假， 如果有，覆盖
            # if leave_detail_dict.get(date):
            #     if leave_detail_dict.get(date).get('leave_detail_time_start') is not None:
            #         check_in = leave_detail_dict.get(date)['leave_detail_time_start']
            #         check_in_type = leave_detail_dict.get(date)['leave_detail_time_start_type']
            #     if leave_detail_dict.get(date).get('leave_detail_time_end') is not None:
            #         check_out = leave_detail_dict.get(date)['leave_detail_time_end']
            #         check_out_type = leave_detail_dict.get(date)['leave_detail_time_end_type']
            # attendance_info_tmp = ExceptionAttendanceInfo(emp=emp, attendance_date=date, check_in=check_in,
            #                                               check_out=check_out, check_in_type=check_in_type,
            #                                               check_out_type=check_out_type,
            #                                               shift_info=shift_info_dict[shift_name]).attendance_info_ins()
        #         attendance_info_tmp = {
        #             'emp_id': emp.id,
        #             'attendance_date': date,
        #             'check_in': check_in,
        #             'check_out': check_out,
        #             'check_in_type': check_in_type,
        #             'check_out_type': check_out_type,
        #             'shift_info': shift_info_dict[shift_name]).attendance_info_ins()
        #         }
        #         attendance_info_list.append(attendance_info_tmp)
        # self.env['attendance.info'].create(attendance_info_list)

    def attendance_total_cal(self, emp_list, start_date, end_date):
        """
        考勤汇总计算
        :return:
        """
        self.ensure_one()
        # 生成考勤日报表
        self.attendance_cal(emp_list, start_date, end_date)
        attendance_total_ins_list = []
        for emp in emp_list.with_progress(msg="正在进行考勤汇总计算"):
            # 获取年月，取得区间月份
            month = 0
            if end_date.year - start_date.year == 0:
                month = end_date.month - start_date.month
            elif end_date.year - start_date.year >= 1:
                month = end_date.month - start_date.month + (end_date.year - start_date.year) * 12
            start_date_tmp = start_date.replace(day=1)
            for num in range(month + 1):
                current_month_num = calendar.monthrange(start_date_tmp.year, start_date_tmp.month)[1]
                # 删除原有记录
                del_question_start = self.env['wage.employee.attendance.annal'].sudo().search(
                    [('employee_id', '=', emp.id), ('attend_code', '=', start_date_tmp.strftime('%Y/%m'))])
                if del_question_start:
                    del_question_start.sudo().unlink()
                attendance_info_dict_list = self.env['attendance.info'].sudo().search([('employee_id', '=', emp.id), (
                    'workDate', '>=', start_date_tmp), ('workDate', '<=', start_date_tmp.replace(day=current_month_num))])
                # check_status_choice = (('0', '正常'), ('1', '迟到'), ('2', '早退'), ('3', '旷工'))
                logging.info(">>>获取的考勤结果:%s", attendance_info_dict_list)
                attendance_total_ins = self.attendance_total_cal_sum(emp, start_date_tmp, attendance_info_dict_list)
                attendance_total_ins_list.append(attendance_total_ins)
                start_date_tmp += timedelta(days=current_month_num)
        self.env['wage.employee.attendance.annal'].sudo().create(attendance_total_ins_list)

    @api.multi
    def attendance_total_cal_sum(self, emp, start_date, attendance_info_dict_list):
        """
        统计月应出勤及请假天数
        :retur
        """
        notsigned_attendance_num = late_attendance_num = early_attendance_num = 0
        work_overtime_hour = weekend_overtime_hour = holiday_overtime_hour = 0
        arrive_total = real_arrive_total = 0
        leave_absence_hour = sick_absence_hour = 0
        leave_dict = {'病假': 0, '事假': 0, '年假': 0, '婚假': 0, '丧假': 0, '陪产假': 0, '产假': 0, '工伤假': 0, '探亲假': 0, '出差（请假）': 0,
                      '其他假': 0}
        for one in attendance_info_dict_list:
            # 统计平时加班、周末加班、节假日加班时数
            if one.attendance_date_status == '00' and one.worked_hours > one.base_work_hours:
                work_overtime_hour = work_overtime_hour + one.worked_hours - one.base_work_hours
            elif one.attendance_date_status == '01':
                weekend_overtime_hour = weekend_overtime_hour + one.worked_hours
            elif one.attendance_date_status == '02':
                holiday_overtime_hour = holiday_overtime_hour + one.worked_hours
            # 统计迟到早退缺卡次数
            if one.on_timeResult == 'NotSigned':
                notsigned_attendance_num = notsigned_attendance_num + 1
            elif one.on_timeResult == 'Late':
                late_attendance_num = late_attendance_num + 1
            if one.off_timeResult == 'NotSigned':  # todo 请假也显示未打卡要排除
                notsigned_attendance_num = notsigned_attendance_num + 1
            elif one.off_timeResult == 'Early':
                early_attendance_num = early_attendance_num + 1
            # 统计请假小时（暂时都当成事假）
            if one.leave_hours:
                leave_absence_hour = leave_absence_hour + one.leave_hours
            # # 统计假期
            # if leave_dict.get(one.check_in_type_id) is not None:
            #     leave_dict[one.check_in_type_id] += 1
            # # 实到天数 real_arrive_total 非请假的所有出勤天数
            # elif one.attendance_date_status:
            #     if one.on_timeResult != 'NotSigned':
            #         real_arrive_total = real_arrive_total + 1
            # # if leave_dict.get(one.check_out_type_id) is not None:
            # #     leave_dict[one.check_out_type_id] = leave_dict[one.check_out_type_id] + 1
            # # 实到天数 real_arrive_total 非请假的所有出勤天数
            # elif one.attendance_date_status:
            #     if one.off_timeResult != 'NotSigned':
            #         real_arrive_total = real_arrive_total + 1

        attendance_total_ins = {'employee_id': emp.id,
                                'attendance_month': start_date,
                                'arrive_total': arrive_total,
                                'real_arrive_total': real_arrive_total,
                                'work_overtime_hour': work_overtime_hour,
                                'weekend_overtime_hour': weekend_overtime_hour,
                                'holiday_overtime_hour': holiday_overtime_hour,
                                'notsigned_attendance_num': notsigned_attendance_num,
                                'late_attendance_num': late_attendance_num,
                                'early_attendance_num': early_attendance_num,
                                'leave_absence_hour': leave_absence_hour,
                                'sick_leave_total': leave_dict['病假'],
                                'personal_leave_total': leave_dict['事假'],
                                'annual_leave_total': leave_dict['年假'],
                                'marriage_leave_total': leave_dict['婚假'],
                                'bereavement_leave_total': leave_dict['丧假'],
                                'paternity_leave_total': leave_dict['陪产假'],
                                'maternity_leave_total': leave_dict['产假'],
                                'work_related_injury_leave_total': leave_dict['工伤假'],
                                'home_leave_total': leave_dict['探亲假'],
                                'travelling_total': leave_dict['出差（请假）'],
                                'other_leave_total': leave_dict['其他假'],
                                }
        return attendance_total_ins


# class LeaveInfo(models.Model):
#     _description = '假期信息表'
#     _name = 'leave.info'
#     _rec_name = 'emp_id'

#     emp_id = fields.Mnay2one('hr.employee', string='员工')
#     start_date = fields.Date('开始日期')
#     leave_info_time_start = fields.Datetime('请假开始时间')
#     end_date = fields.Date('结束日期')
#     leave_info_time_end = fields.Datetime('请假结束时间')
#     # leave_type = fields.Many2one('leave.type', string='假期类型')
#     # leave_info_status = fields.Char('假期单据状态', selection=user_status_choice)


# class LeaveDetail(models.Model):
#     _description = '假期明细表'
#     _name = 'leave.detail'
#     _rec_name = 'leave_info_id'

#     emp_id = fields.Mnay2one('hr.employee.info', string='员工')
#     leave_info_id = fields.Many2one('leave.info', string='单据主键')
#     leave_date = fields.Date('请假日期')
#     leave_detail_time_start = fields.Datetime('请假开始时间', null=True, blank=True)
#     leave_detail_time_end = fields.Datetime('请假结束时间', null=True, blank=True)
#     # leave_type = fields.Many2one('leave.type', string='假期类型')
#     leave_info_status = fields.Char('假期明细单据状态', selection=status_choice)
#     count_length = fields.Float('长度统计')

    # @api.multi
    # def get_leave_detail_dict(self, emp_one, start_date, end_date):
    #     """
    #     处理请假数据
    #     """
    #     # 对 假期的 开始日期小于考勤计算的结束日期 或 假期的 结束日期大于考勤计算的起始日期

    #     leave_info_list = self.env['leave.info'].sudo().search(
    #         [('emp_id', '=', emp_one.id), ('start_date', '<=', end_date), ('end_date', '>=', start_date)])
    #     # 判定在统计期间是否有请假记录
    #     if len(leave_info_list):
    #         self.leave_split_cal(leave_info_list)
    #     leave_detail_dict = {}
    #     leave_detail_list = self.env['leave.detail'].sudo().search(
    #         [('emp_id', '=', emp_one.id), ('leave_date', '<=', end_date), ('leave_date', '>=', start_date), ('leave_info_status', '=', '1')])
    #     for one in leave_detail_list:
    #         # leave_detail_dict[one.leave_date] = one
    #         if leave_detail_dict.get(one.leave_date) is None:
    #             leave_detail_dict[one.leave_date] = {}
    #         if one.leave_detail_time_start is not None:
    #             if leave_detail_dict[one.leave_date].get('leave_detail_time_start') is None:
    #                 leave_detail_dict[one.leave_date]['leave_detail_time_start'] = one.leave_detail_time_start
    #                 leave_detail_dict[one.leave_date]['leave_detail_time_start_type'] = one.leave_type
    #             else:
    #                 raise UserError("存在重复记录-{name}的{attendance_date}存在重复的请假数据".format(name=one.emp.name,
    #                                                                                   attendance_date=one.leave_date))
    #         if one.leave_detail_time_end is not None:
    #             if leave_detail_dict[one.leave_date].get('leave_detail_time_end') is None:
    #                 leave_detail_dict[one.leave_date]['leave_detail_time_end'] = one.leave_detail_time_end
    #                 leave_detail_dict[one.leave_date]['leave_detail_time_end_type'] = one.leave_type
    #             else:
    #                 raise UserError("存在重复记录-{name}的{attendance_date}存在重复的请假数据".format(name=one.emp.name,
    #                                                                                   attendance_date=one.leave_date))
    #     return leave_detail_dict

    # def leave_split_cal(self, queryset):
    #     """
    #     创建假期明细表
    #     """
    #     leave_detail_ins_list = []
    #     for leave_info_ins in queryset:
    #         leave_split_list = self.leave_split(leave_info_ins)
    #         if len(leave_split_list):
    #             leave_detail_ins_list += leave_split_list
    #     self.env['leave.detail'].create(leave_detail_ins_list)

    # def leave_split(self, leave_info_ins):
    #     """
    #     假期拆分，根据排班表拆分
    #     """
    #     leave_detail_ins_list = []
    #     # 获取班次信息
    #     shift_info_dict = self.get_shift_info_dict()

    #     # 删除已经存在的相关假期明细
    #     self.env['leave.detail'].sudo().search([('leave_info_id', '=', leave_info_ins.id)]).unlink()
    #     # 获取人员排班表
    #     scheduling_info_dict = self.get_scheduling_info_dict(leave_info_ins.emp, leave_info_ins.start_date,
    #                                                          leave_info_ins.end_date)

    #     # scheduling_info_dict[one.plan_check_time] = one.class_id
    #     for attendance_date, shift_name in scheduling_info_dict.items():
    #         # 假期类型不含节假日
    #         if leave_info_ins.leave_type.legal_include is False:
    #             # 班次为节假日，跳过
    #             if shift_info_dict[shift_name].type_shift is False:
    #                 continue
    #         leave_detail_ins = LeaveDetail()
    #         leave_detail_ins.emp = leave_info_ins.emp
    #         leave_detail_ins.leave_info_id = leave_info_ins
    #         leave_detail_ins.leave_date = attendance_date
    #         # 当前日期不是第一天 或最后一天 ，开始日期和结束日期为 班次的 上午上班时间、 下午下班时间
    #         leave_detail_ins.leave_detail_time_start = shift_info_dict[shift_name].check_in
    #         leave_detail_ins.leave_detail_time_end = shift_info_dict[shift_name].check_out
    #         # 当前日期为开始日期
    #         if attendance_date == leave_info_ins.start_date:
    #             # 开始时间小于 check_in_end 则 开始请假时间 为早上
    #             if leave_info_ins.leave_info_time_start <= shift_info_dict[shift_name].check_in_end:
    #                 leave_detail_ins.leave_detail_time_start = leave_info_ins.leave_info_time_start
    #             # 开始时间大于 check_out_start 则 开始请假时间 为下午
    #             elif leave_info_ins.leave_info_time_start >= shift_info_dict[shift_name].check_out_start:
    #                 leave_detail_ins.leave_detail_time_start = None
    #             # 否则报错
    #             else:
    #                 raise UserError("假期起始时间不正确")
    #         # 当前日期为结束日期
    #         if attendance_date == leave_info_ins.end_date:
    #             # leave_info_time_end 小于 check_in_end 则 结束请假时间为早上
    #             if leave_info_ins.leave_info_time_end <= shift_info_dict[shift_name].check_in_end:
    #                 leave_detail_ins.leave_detail_time_end = None
    #             # leave_info_time_end 大于 check_out_start 则 结束请假时间为下午
    #             elif leave_info_ins.leave_info_time_end >= shift_info_dict[shift_name].check_out_start:
    #                 leave_detail_ins.leave_detail_time_end = leave_info_ins.leave_info_time_end
    #             else:
    #                 raise UserError("假期结束时间不正确")
    #         leave_detail_ins.leave_type = leave_info_ins.leave_type
    #         leave_detail_ins.leave_info_status = leave_info_ins.leave_info_status
    #         #  判断是否有重复单据
    #         # self.leave_info_distinct(leave_detail_ins)
    #         # leave_detail_ins.count_length = float((0 if leave_detail_ins.leave_detail_time_start is None else 0.5) + (
    #         #     0 if leave_detail_ins.leave_detail_time_end is None else 0.5))
    #         leave_detail_ins_list.append(leave_detail_ins)
    #     return leave_detail_ins_list

    # def leave_info_distinct(self, leave_detail_ins_tmp):
    #     """
    #     检查重复记录
    #     """
    #     # 上午/下午  全天  上午  下午 无 ,共5种情况 不需要初始化 attendance_date
    #     leave_detail_ins_list = self.env['leave.detail'].sudo().search([('emp_id', '=', leave_detail_ins_tmp.emp_id), (
    #         'leave_date', '=', leave_detail_ins_tmp.leave_date), ('leave_info_status', '=', leave_detail_ins_tmp.leave_info_status)])
    #     attendance_date = {}
    #     for one in leave_detail_ins_list:
    #         if one.leave_detail_time_start is not None:
    #             if attendance_date.get('leave_detail_time_start') is None:
    #                 attendance_date['leave_detail_time_start'] = one.leave_detail_time_start
    #             else:
    #                 raise UserError("上午存在重复记录")
    #         if one.leave_detail_time_end is not None:
    #             if attendance_date.get('leave_detail_time_end') is None:
    #                 attendance_date['leave_detail_time_end'] = one.leave_detail_time_end
    #             else:
    #                 raise UserError("下午存在重复记录")
    #         if attendance_date.get(
    #                 'leave_detail_time_start') is not None and leave_detail_ins_tmp.leave_detail_time_start is not None:
    #             raise UserError("存在重复记录，已有{date}上午的请假单".format(date=leave_detail_ins_tmp.leave_date))
    #         if attendance_date.get(
    #                 'leave_detail_time_end') is not None and leave_detail_ins_tmp.leave_detail_time_end is not None:
    #             raise UserError("存在重复记录，已有{date}下午的请假单".format(date=leave_detail_ins_tmp.leave_date))

    # cr.execute("select inv.name,inv.state,inv.id,inv.number from account_invoice inv where inv.state!='paid' and id in %s", (tuple(reconciled_inv()),))
    # res = cr.dictfetchall()
    # result = res
    # cr.dictfetchall() will give you [{'reg_no': 123},{'reg_no': 543},].
    # cr.dictfetchone() will give you {'reg_no': 123}.
    # cr.fetchall() will give you '[(123),(543)]'.
    # cr.fetchone() will give you '(123)'.

    # # 获取班次信息
    # def get_shift_info_dict(self):
    #     shift_info_dict = {}
    #     shift_info_list = self.env['dingding.simple.groups.list'].sudo().search([])
    #     for one in shift_info_list:
    #         shift_info_dict[one.class_name] = one
    #     return shift_info_dict

    # # 获取人员排班信息
    # def get_scheduling_info_dict(self, emp_one, start_date, end_date):
    #     scheduling_info_dict = {}
    #     scheduling_info_list_query = self.env['hr.dingding.plan'].sudo().search(
    #         [('user_id', '=', emp_one.id), ('plan_check_time', '>=', start_date), ('plan_check_time', '<=', end_date)])
    #     for one in scheduling_info_list_query:
    #         scheduling_info_dict[one.plan_check_time] = one.class_id
    #     return scheduling_info_dict


class WageEmpPerformanceManage(models.TransientModel):
    _description = '从绩效计算结果'
    _name = 'wage.employee.performance.manage.transient'

    start_date = fields.Date(string=u'开始日期', required=True)
    end_date = fields.Date(string=u'结束日期', required=True)

    @api.multi
    def compute_performance_result(self):
        """
        从绩效计算结果
        :return:
        """
        self.ensure_one()
        # raise UserError("暂未实现！！！")
        return {'type': 'ir.actions.act_window_close'}
