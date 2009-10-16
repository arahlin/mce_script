; This file is automatically generated by mas_param!

function str_flat,a
    if n_elements(a) eq 0 then return,''
    s = strcompress(string(a[0]))
    for i=1,n_elements(a)-1 do begin
        s=s+' '+strcompress(string(a[i]))
    endfor
    return,s
end

pro save_exp_params,m,filename
    spawn,'mas_param -s '+filename+' set array_id "'+str_flat(m.array_id)+'"'
    spawn,'mas_param -s '+filename+' set array_width '+str_flat(m.array_width)
    spawn,'mas_param -s '+filename+' set hardware_rc '+str_flat(m.hardware_rc)
    spawn,'mas_param -s '+filename+' set hardware_sync '+str_flat(m.hardware_sync)
    spawn,'mas_param -s '+filename+' set hardware_bac '+str_flat(m.hardware_bac)
    spawn,'mas_param -s '+filename+' set hardware_rect '+str_flat(m.hardware_rect)
    spawn,'mas_param -s '+filename+' set hardware_rc_data '+str_flat(m.hardware_rc_data)
    spawn,'mas_param -s '+filename+' set sb0_select_clk '+str_flat(m.sb0_select_clk)
    spawn,'mas_param -s '+filename+' set sb0_use_dv '+str_flat(m.sb0_use_dv)
    spawn,'mas_param -s '+filename+' set sb0_use_sync '+str_flat(m.sb0_use_sync)
    spawn,'mas_param -s '+filename+' set sb1_select_clk '+str_flat(m.sb1_select_clk)
    spawn,'mas_param -s '+filename+' set sb1_use_dv '+str_flat(m.sb1_use_dv)
    spawn,'mas_param -s '+filename+' set sb1_use_sync '+str_flat(m.sb1_use_sync)
    spawn,'mas_param -s '+filename+' set default_num_rows '+str_flat(m.default_num_rows)
    spawn,'mas_param -s '+filename+' set default_sample_num '+str_flat(m.default_sample_num)
    spawn,'mas_param -s '+filename+' set default_data_mode '+str_flat(m.default_data_mode)
    spawn,'mas_param -s '+filename+' set default_flux_jumping '+str_flat(m.default_flux_jumping)
    spawn,'mas_param -s '+filename+' set default_servo_p '+str_flat(m.default_servo_p)
    spawn,'mas_param -s '+filename+' set default_servo_i '+str_flat(m.default_servo_i)
    spawn,'mas_param -s '+filename+' set default_servo_d '+str_flat(m.default_servo_d)
    spawn,'mas_param -s '+filename+' set default_sa_bias '+str_flat(m.default_sa_bias)
    spawn,'mas_param -s '+filename+' set default_sq2_bias '+str_flat(m.default_sq2_bias)
    spawn,'mas_param -s '+filename+' set default_sq1_bias '+str_flat(m.default_sq1_bias)
    spawn,'mas_param -s '+filename+' set default_sq1_bias_off '+str_flat(m.default_sq1_bias_off)
    spawn,'mas_param -s '+filename+' set columns_off '+str_flat(m.columns_off)
    spawn,'mas_param -s '+filename+' set stop_after_sq1_servo '+str_flat(m.stop_after_sq1_servo)
    spawn,'mas_param -s '+filename+' set sa_offset_bias_ratio '+str_flat(m.sa_offset_bias_ratio)
    spawn,'mas_param -s '+filename+' set sa_flux_quanta '+str_flat(m.sa_flux_quanta)
    spawn,'mas_param -s '+filename+' set sa_ramp_bias '+str_flat(m.sa_ramp_bias)
    spawn,'mas_param -s '+filename+' set sa_ramp_flux_start '+str_flat(m.sa_ramp_flux_start)
    spawn,'mas_param -s '+filename+' set sa_ramp_flux_count '+str_flat(m.sa_ramp_flux_count)
    spawn,'mas_param -s '+filename+' set sa_ramp_flux_step '+str_flat(m.sa_ramp_flux_step)
    spawn,'mas_param -s '+filename+' set sa_ramp_bias_start '+str_flat(m.sa_ramp_bias_start)
    spawn,'mas_param -s '+filename+' set sa_ramp_bias_step '+str_flat(m.sa_ramp_bias_step)
    spawn,'mas_param -s '+filename+' set sa_ramp_bias_count '+str_flat(m.sa_ramp_bias_count)
    spawn,'mas_param -s '+filename+' set sq2_rows '+str_flat(m.sq2_rows)
    spawn,'mas_param -s '+filename+' set sq2servo_gain '+str_flat(m.sq2servo_gain)
    spawn,'mas_param -s '+filename+' set sq1servo_gain '+str_flat(m.sq1servo_gain)
    spawn,'mas_param -s '+filename+' set sq2_servo_flux_start '+str_flat(m.sq2_servo_flux_start)
    spawn,'mas_param -s '+filename+' set sq2_servo_flux_count '+str_flat(m.sq2_servo_flux_count)
    spawn,'mas_param -s '+filename+' set sq2_servo_flux_step '+str_flat(m.sq2_servo_flux_step)
    spawn,'mas_param -s '+filename+' set sq1_servo_flux_start '+str_flat(m.sq1_servo_flux_start)
    spawn,'mas_param -s '+filename+' set sq1_servo_flux_count '+str_flat(m.sq1_servo_flux_count)
    spawn,'mas_param -s '+filename+' set sq1_servo_flux_step '+str_flat(m.sq1_servo_flux_step)
    spawn,'mas_param -s '+filename+' set sq2_servo_bias_ramp '+str_flat(m.sq2_servo_bias_ramp)
    spawn,'mas_param -s '+filename+' set sq2_servo_bias_start '+str_flat(m.sq2_servo_bias_start)
    spawn,'mas_param -s '+filename+' set sq2_servo_bias_count '+str_flat(m.sq2_servo_bias_count)
    spawn,'mas_param -s '+filename+' set sq2_servo_bias_step '+str_flat(m.sq2_servo_bias_step)
    spawn,'mas_param -s '+filename+' set sq1_servo_all_rows '+str_flat(m.sq1_servo_all_rows)
    spawn,'mas_param -s '+filename+' set sq1ramp_plot_rows '+str_flat(m.sq1ramp_plot_rows)
    spawn,'mas_param -s '+filename+' set locktest_plot_row '+str_flat(m.locktest_plot_row)
    spawn,'mas_param -s '+filename+' set sq1_ramp_flux_start '+str_flat(m.sq1_ramp_flux_start)
    spawn,'mas_param -s '+filename+' set sq1_ramp_flux_step '+str_flat(m.sq1_ramp_flux_step)
    spawn,'mas_param -s '+filename+' set sq1_ramp_flux_count '+str_flat(m.sq1_ramp_flux_count)
    spawn,'mas_param -s '+filename+' set locktest_pass_amplitude '+str_flat(m.locktest_pass_amplitude)
    spawn,'mas_param -s '+filename+' set sq1servo_slope '+str_flat(m.sq1servo_slope)
    spawn,'mas_param -s '+filename+' set sq2servo_slope '+str_flat(m.sq2servo_slope)
    spawn,'mas_param -s '+filename+' set sq1_ramp_tes_bias '+str_flat(m.sq1_ramp_tes_bias)
    spawn,'mas_param -s '+filename+' set sq1_ramp_tes_bias_start '+str_flat(m.sq1_ramp_tes_bias_start)
    spawn,'mas_param -s '+filename+' set sq1_ramp_tes_bias_step '+str_flat(m.sq1_ramp_tes_bias_step)
    spawn,'mas_param -s '+filename+' set sq1_ramp_tes_bias_count '+str_flat(m.sq1_ramp_tes_bias_count)
    spawn,'mas_param -s '+filename+' set tes_bias_idle '+str_flat(m.tes_bias_idle)
    spawn,'mas_param -s '+filename+' set tes_bias_normal '+str_flat(m.tes_bias_normal)
    spawn,'mas_param -s '+filename+' set tes_bias_normal_time '+str_flat(m.tes_bias_normal_time)
    spawn,'mas_param -s '+filename+' set tes_bias_do_reconfig '+str_flat(m.tes_bias_do_reconfig)
    spawn,'mas_param -s '+filename+' set sq2servo_safb_init '+str_flat(m.sq2servo_safb_init)
    spawn,'mas_param -s '+filename+' set sq1servo_sq2fb_init '+str_flat(m.sq1servo_sq2fb_init)
    spawn,'mas_param -s '+filename+' set ramp_tes_start '+str_flat(m.ramp_tes_start)
    spawn,'mas_param -s '+filename+' set ramp_tes_step '+str_flat(m.ramp_tes_step)
    spawn,'mas_param -s '+filename+' set ramp_tes_count '+str_flat(m.ramp_tes_count)
    spawn,'mas_param -s '+filename+' set ramp_tes_final_bias '+str_flat(m.ramp_tes_final_bias)
    spawn,'mas_param -s '+filename+' set ramp_tes_initial_pause '+str_flat(m.ramp_tes_initial_pause)
    spawn,'mas_param -s '+filename+' set ramp_tes_period_us '+str_flat(m.ramp_tes_period_us)
    spawn,'mas_param -s '+filename+' set iv_data_mode '+str_flat(m.iv_data_mode)
    spawn,'mas_param -s '+filename+' set bias_line_card '+str_flat(m.bias_line_card)
    spawn,'mas_param -s '+filename+' set bias_line_para '+str_flat(m.bias_line_para)
    spawn,'mas_param -s '+filename+' set config_rc '+str_flat(m.config_rc)
    spawn,'mas_param -s '+filename+' set config_sync '+str_flat(m.config_sync)
    spawn,'mas_param -s '+filename+' set config_fast_sq2 '+str_flat(m.config_fast_sq2)
    spawn,'mas_param -s '+filename+' set config_dead_tes '+str_flat(m.config_dead_tes)
    spawn,'mas_param -s '+filename+' set data_rate '+str_flat(m.data_rate)
    spawn,'mas_param -s '+filename+' set row_len '+str_flat(m.row_len)
    spawn,'mas_param -s '+filename+' set num_rows '+str_flat(m.num_rows)
    spawn,'mas_param -s '+filename+' set num_rows_reported '+str_flat(m.num_rows_reported)
    spawn,'mas_param -s '+filename+' set readout_row_index '+str_flat(m.readout_row_index)
    spawn,'mas_param -s '+filename+' set sample_dly '+str_flat(m.sample_dly)
    spawn,'mas_param -s '+filename+' set sample_num '+str_flat(m.sample_num)
    spawn,'mas_param -s '+filename+' set fb_dly '+str_flat(m.fb_dly)
    spawn,'mas_param -s '+filename+' set row_dly '+str_flat(m.row_dly)
    spawn,'mas_param -s '+filename+' set data_mode '+str_flat(m.data_mode)
    spawn,'mas_param -s '+filename+' set flux_jumping '+str_flat(m.flux_jumping)
    spawn,'mas_param -s '+filename+' set servo_mode '+str_flat(m.servo_mode)
    spawn,'mas_param -s '+filename+' set servo_p '+str_flat(m.servo_p)
    spawn,'mas_param -s '+filename+' set servo_i '+str_flat(m.servo_i)
    spawn,'mas_param -s '+filename+' set servo_d '+str_flat(m.servo_d)
    spawn,'mas_param -s '+filename+' set dead_detectors '+str_flat(m.dead_detectors)
    spawn,'mas_param -s '+filename+' set tes_bias '+str_flat(m.tes_bias)
    spawn,'mas_param -s '+filename+' set row_order '+str_flat(m.row_order)
    spawn,'mas_param -s '+filename+' set config_flux_quanta_all '+str_flat(m.config_flux_quanta_all)
    spawn,'mas_param -s '+filename+' set flux_quanta '+str_flat(m.flux_quanta)
    spawn,'mas_param -s '+filename+' set flux_quanta_all '+str_flat(m.flux_quanta_all)
    spawn,'mas_param -s '+filename+' set fb_const '+str_flat(m.fb_const)
    spawn,'mas_param -s '+filename+' set sq1_bias '+str_flat(m.sq1_bias)
    spawn,'mas_param -s '+filename+' set sq1_bias_off '+str_flat(m.sq1_bias_off)
    spawn,'mas_param -s '+filename+' set sq2_bias '+str_flat(m.sq2_bias)
    spawn,'mas_param -s '+filename+' set sq2_fb '+str_flat(m.sq2_fb)
    spawn,'mas_param -s '+filename+' set sq2_fb_set '+str_flat(m.sq2_fb_set)
    spawn,'mas_param -s '+filename+' set sa_bias '+str_flat(m.sa_bias)
    spawn,'mas_param -s '+filename+' set sa_fb '+str_flat(m.sa_fb)
    spawn,'mas_param -s '+filename+' set sa_offset '+str_flat(m.sa_offset)
    spawn,'mas_param -s '+filename+' set config_adc_offset_all '+str_flat(m.config_adc_offset_all)
    spawn,'mas_param -s '+filename+' set adc_offset_c '+str_flat(m.adc_offset_c)
    spawn,'mas_param -s '+filename+' set adc_offset_cr '+str_flat(m.adc_offset_cr)
end


pro load_exp_params,filename,m
    m = create_struct('_source',filename,  $
        'array_id',mas_param_string(filename,'array_id'),  $
        'array_width',mas_param_int(filename,'array_width'),  $
        'hardware_rc',mas_param_int(filename,'hardware_rc'),  $
        'hardware_sync',mas_param_int(filename,'hardware_sync'),  $
        'hardware_bac',mas_param_int(filename,'hardware_bac'),  $
        'hardware_rect',mas_param_int(filename,'hardware_rect'),  $
        'hardware_rc_data',mas_param_int(filename,'hardware_rc_data'),  $
        'sb0_select_clk',mas_param_int(filename,'sb0_select_clk'),  $
        'sb0_use_dv',mas_param_int(filename,'sb0_use_dv'),  $
        'sb0_use_sync',mas_param_int(filename,'sb0_use_sync'),  $
        'sb1_select_clk',mas_param_int(filename,'sb1_select_clk'),  $
        'sb1_use_dv',mas_param_int(filename,'sb1_use_dv'),  $
        'sb1_use_sync',mas_param_int(filename,'sb1_use_sync'),  $
        'default_num_rows',mas_param_int(filename,'default_num_rows'),  $
        'default_sample_num',mas_param_int(filename,'default_sample_num'),  $
        'default_data_mode',mas_param_int(filename,'default_data_mode'),  $
        'default_flux_jumping',mas_param_int(filename,'default_flux_jumping'),  $
        'default_servo_p',mas_param_int(filename,'default_servo_p'),  $
        'default_servo_i',mas_param_int(filename,'default_servo_i'),  $
        'default_servo_d',mas_param_int(filename,'default_servo_d'),  $
        'default_sa_bias',mas_param_int(filename,'default_sa_bias'),  $
        'default_sq2_bias',mas_param_int(filename,'default_sq2_bias'),  $
        'default_sq1_bias',mas_param_int(filename,'default_sq1_bias'),  $
        'default_sq1_bias_off',mas_param_int(filename,'default_sq1_bias_off'),  $
        'columns_off',mas_param_int(filename,'columns_off'),  $
        'stop_after_sq1_servo',mas_param_int(filename,'stop_after_sq1_servo'),  $
        'sa_offset_bias_ratio',mas_param_float(filename,'sa_offset_bias_ratio'),  $
        'sa_flux_quanta',mas_param_int(filename,'sa_flux_quanta'),  $
        'sa_ramp_bias',mas_param_int(filename,'sa_ramp_bias'),  $
        'sa_ramp_flux_start',mas_param_int(filename,'sa_ramp_flux_start'),  $
        'sa_ramp_flux_count',mas_param_int(filename,'sa_ramp_flux_count'),  $
        'sa_ramp_flux_step',mas_param_int(filename,'sa_ramp_flux_step'),  $
        'sa_ramp_bias_start',mas_param_int(filename,'sa_ramp_bias_start'),  $
        'sa_ramp_bias_step',mas_param_int(filename,'sa_ramp_bias_step'),  $
        'sa_ramp_bias_count',mas_param_int(filename,'sa_ramp_bias_count'),  $
        'sq2_rows',mas_param_int(filename,'sq2_rows'),  $
        'sq2servo_gain',mas_param_float(filename,'sq2servo_gain'),  $
        'sq1servo_gain',mas_param_float(filename,'sq1servo_gain'),  $
        'sq2_servo_flux_start',mas_param_int(filename,'sq2_servo_flux_start'),  $
        'sq2_servo_flux_count',mas_param_int(filename,'sq2_servo_flux_count'),  $
        'sq2_servo_flux_step',mas_param_int(filename,'sq2_servo_flux_step'),  $
        'sq1_servo_flux_start',mas_param_int(filename,'sq1_servo_flux_start'),  $
        'sq1_servo_flux_count',mas_param_int(filename,'sq1_servo_flux_count'),  $
        'sq1_servo_flux_step',mas_param_int(filename,'sq1_servo_flux_step'),  $
        'sq2_servo_bias_ramp',mas_param_int(filename,'sq2_servo_bias_ramp'),  $
        'sq2_servo_bias_start',mas_param_int(filename,'sq2_servo_bias_start'),  $
        'sq2_servo_bias_count',mas_param_int(filename,'sq2_servo_bias_count'),  $
        'sq2_servo_bias_step',mas_param_int(filename,'sq2_servo_bias_step'),  $
        'sq1_servo_all_rows',mas_param_int(filename,'sq1_servo_all_rows'),  $
        'sq1ramp_plot_rows',mas_param_int(filename,'sq1ramp_plot_rows'),  $
        'locktest_plot_row',mas_param_int(filename,'locktest_plot_row'),  $
        'sq1_ramp_flux_start',mas_param_int(filename,'sq1_ramp_flux_start'),  $
        'sq1_ramp_flux_step',mas_param_int(filename,'sq1_ramp_flux_step'),  $
        'sq1_ramp_flux_count',mas_param_int(filename,'sq1_ramp_flux_count'),  $
        'locktest_pass_amplitude',mas_param_int(filename,'locktest_pass_amplitude'),  $
        'sq1servo_slope',mas_param_int(filename,'sq1servo_slope'),  $
        'sq2servo_slope',mas_param_int(filename,'sq2servo_slope'),  $
        'sq1_ramp_tes_bias',mas_param_int(filename,'sq1_ramp_tes_bias'),  $
        'sq1_ramp_tes_bias_start',mas_param_int(filename,'sq1_ramp_tes_bias_start'),  $
        'sq1_ramp_tes_bias_step',mas_param_int(filename,'sq1_ramp_tes_bias_step'),  $
        'sq1_ramp_tes_bias_count',mas_param_int(filename,'sq1_ramp_tes_bias_count'),  $
        'tes_bias_idle',mas_param_int(filename,'tes_bias_idle'),  $
        'tes_bias_normal',mas_param_int(filename,'tes_bias_normal'),  $
        'tes_bias_normal_time',mas_param_int(filename,'tes_bias_normal_time'),  $
        'tes_bias_do_reconfig',mas_param_int(filename,'tes_bias_do_reconfig'),  $
        'sq2servo_safb_init',mas_param_int(filename,'sq2servo_safb_init'),  $
        'sq1servo_sq2fb_init',mas_param_int(filename,'sq1servo_sq2fb_init'),  $
        'ramp_tes_start',mas_param_int(filename,'ramp_tes_start'),  $
        'ramp_tes_step',mas_param_int(filename,'ramp_tes_step'),  $
        'ramp_tes_count',mas_param_int(filename,'ramp_tes_count'),  $
        'ramp_tes_final_bias',mas_param_int(filename,'ramp_tes_final_bias'),  $
        'ramp_tes_initial_pause',mas_param_int(filename,'ramp_tes_initial_pause'),  $
        'ramp_tes_period_us',mas_param_int(filename,'ramp_tes_period_us'),  $
        'iv_data_mode',mas_param_int(filename,'iv_data_mode'),  $
        'bias_line_card',mas_param_int(filename,'bias_line_card'),  $
        'bias_line_para',mas_param_int(filename,'bias_line_para'),  $
        'config_rc',mas_param_int(filename,'config_rc'),  $
        'config_sync',mas_param_int(filename,'config_sync'),  $
        'config_fast_sq2',mas_param_int(filename,'config_fast_sq2'),  $
        'config_dead_tes',mas_param_int(filename,'config_dead_tes'),  $
        'data_rate',mas_param_int(filename,'data_rate'),  $
        'row_len',mas_param_int(filename,'row_len'),  $
        'num_rows',mas_param_int(filename,'num_rows'),  $
        'num_rows_reported',mas_param_int(filename,'num_rows_reported'),  $
        'readout_row_index',mas_param_int(filename,'readout_row_index'),  $
        'sample_dly',mas_param_int(filename,'sample_dly'),  $
        'sample_num',mas_param_int(filename,'sample_num'),  $
        'fb_dly',mas_param_int(filename,'fb_dly'),  $
        'row_dly',mas_param_int(filename,'row_dly'),  $
        'data_mode',mas_param_int(filename,'data_mode'),  $
        'flux_jumping',mas_param_int(filename,'flux_jumping'),  $
        'servo_mode',mas_param_int(filename,'servo_mode'),  $
        'servo_p',mas_param_int(filename,'servo_p'),  $
        'servo_i',mas_param_int(filename,'servo_i'),  $
        'servo_d',mas_param_int(filename,'servo_d'),  $
        'dead_detectors',mas_param_int(filename,'dead_detectors'),  $
        'tes_bias',mas_param_int(filename,'tes_bias'),  $
        'row_order',mas_param_int(filename,'row_order'),  $
        'config_flux_quanta_all',mas_param_int(filename,'config_flux_quanta_all'),  $
        'flux_quanta',mas_param_int(filename,'flux_quanta'),  $
        'flux_quanta_all',mas_param_int(filename,'flux_quanta_all'),  $
        'fb_const',mas_param_int(filename,'fb_const'),  $
        'sq1_bias',mas_param_int(filename,'sq1_bias'),  $
        'sq1_bias_off',mas_param_int(filename,'sq1_bias_off'),  $
        'sq2_bias',mas_param_int(filename,'sq2_bias'),  $
        'sq2_fb',mas_param_int(filename,'sq2_fb'),  $
        'sq2_fb_set',mas_param_int(filename,'sq2_fb_set'),  $
        'sa_bias',mas_param_int(filename,'sa_bias'),  $
        'sa_fb',mas_param_int(filename,'sa_fb'),  $
        'sa_offset',mas_param_int(filename,'sa_offset'),  $
        'config_adc_offset_all',mas_param_int(filename,'config_adc_offset_all'),  $
        'adc_offset_c',mas_param_int(filename,'adc_offset_c'),  $
        'adc_offset_cr',mas_param_int(filename,'adc_offset_cr')    )
end
