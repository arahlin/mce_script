pro auto_setup_ramp_sa_fb_plot,file_name,RC=rc,interactive=interactive

;  Aug. 21 created by Elia Battistelli (EB) for the auto_setup program
;	   adapted from ramp_sa_fb_plot.pro 


common ramp_sa_var

;Close all open files. It helps avoid some errors although shouldn't be necessary:
close,/all

;Comunication:
print,''
print,'########################################################################################'
print,'#2) The second step is to ramp the SSA bias (together with the SSA fb) for RC'+strcompress(string(RC),/remove_all)+'         #'
print,'#   and choose the bias for which the peak-to-peak of the V-phi curve is maximum.      #'
print,'########################################################################################'
print,''

;Set ramp_sa_file_name
file_name_ramp_sa=file_name+'_ssa'

ctime=string(file_name,format='(i10)')

logfile=ctime+'/'+ctime+'.log'

;Run the shell script:
spawn,'ramp_sa_fb '+file_name_ramp_sa+' '+string(rc)+' 1'+ ' >> /data/cryo/current_data/'+logfile,exit_status=status4
if status4 ne 0 then begin
	print,''
        print,'###############################################################'
        print,'# ERROR! AN ERROR HAS OCCURED WHEN RUNNING THE RAMP_SA SCRIPT #'
        print,'###############################################################'
        print,''
        exit,status=4
endif

;Let's define filenames and folders
current_data = ''
openr, 3, '/data/cryo/current_data_name'
readf, 3, current_data

default_folder = '/data/cryo/' + current_data + '/'
folder=default_folder

full_name=folder+file_name_ramp_sa
plot_file = folder + 'analysis/' + file_name_ramp_sa + '.ps'

;spawn,'ln full_name+' /data/mce_ctimes/'+strmid(file_name_ramp_sa,11)
;spawn,'ln fill_name+'.run /data/mce_ctimes/'+strmid(file_name_ramp_sa,11)+'.run'

;Let's drow

set_plot, 'ps'
device, filename= plot_file, /landscape

nsum = 48

;Setting up factors and captions for engineering and AD units.

;Default is A/D units.
v_factor = 1./1000.
v_units = ' ( x 1000 AD Units)'
i_factor = 1./1000.
i_units = ' ( x 1000 AD Units)'

;Converting SA_bias to current.
vmax = 2500.  ; mV
RL  = 15000.  ; Ohms
full_scale = 65535.   ; Digital fs = 2^16 -1.
ma2uA      = 1000.    ; convert to microamperes

sa_bias = 0 * vmax * ma2uA  / ( RL* full_scale)
    
!p.multi=[0,2,4]            ;Multiple plot parameters.
!p.region=[0,0,0,0]         ;Plot region.
 
;Reading the 2-dim data array from the file:
readin=auto_setup_read_2d_ramp(full_name)  ;Read in file.

;Read labels, loop sizes, etc.
horiz_label=readin.labels[2]
vert_label = readin.labels[1]
card = readin.labels[0]
   
n_bias = readin.specs[0]
bias_start = readin.specs[1]
bias_step =  readin.specs[2]

n_fb = readin.specs[3]
fb_start = readin.specs[4]
fb_step =  readin.specs[5]

;Now, make data arrays of the necessary sizes.

av_vol=fltarr(n_bias, n_fb, 8)     ;Array for mean values.
dev_vol=fltarr(n_bias, n_fb, 8 )    ;Array for error values.
    
;Calculate mean and stdev for the reading column of data for each
;bias value and repeat for all channels.

for j=0,7 do begin
	for m=0,n_bias -1 do begin
		for i=0, n_fb -1 do begin
			result=moment(readin.data(m,i,j,*))
            		av_vol(m,i,j)=result[0]
            		dev_vol(m,i,j)=sqrt(result[1])/ sqrt(nsum)            
        	endfor
    	endfor 
endfor
    
av_vol = av_vol * v_factor
dev_vol = dev_vol * v_factor

;Set up feedback current:
i_fb = i_factor * (  fb_start + findgen(n_fb)*fb_step)

;Automatically find the bias, target and corresponding fb
;we use peak-to-peak merit function

deriv_av_vol=av_vol
sav=size(av_vol)
mean_av_vol=fltarr(sav(2))
flag=intarr(sav(1),sav(3))
flag(*,*)=0
num_zeros=flag
estim_range=fltarr(sav(1),sav(3))
ind=intarr(sav(3))
final_sa_bias_ch_by_ch=lon64arr(sav(3))
target_min_slope_ch_by_ch=lon64arr(sav(3))
fb_min_slope_ch_by_ch=lon64arr(sav(3))
target_half_point_ch_by_ch=lon64arr(sav(3))
fb_half_point_ch_by_ch=lon64arr(sav(3))
SA_target=lon64arr(sav(3))
SA_fb_init=lon64arr(sav(3))
sa_middle=fltarr(sav(1),sav(3))

for bsa=0,sav(1)-1 do begin		;calculate the derivatives of the V-phi plots
	for chan=0,sav(3)-1 do begin
 		deriv_av_vol(bsa,*,chan)=deriv(i_fb(*),av_vol(bsa,*,chan))
	endfor
endfor

for chan=0,sav(3)-1 do begin
	for bsa=0,sav(1)-1 do begin
		;Merit function calculated from the peak-to-peak values
		estim_range(bsa,chan)=max(av_vol(bsa,*,chan))-min(av_vol(bsa,*,chan))
		sa_middle(bsa,chan) = (max(av_vol(bsa,*,chan))+min(av_vol(bsa,*,chan)))/2.
	endfor
endfor

;  Make an n_bias+1 pages set of plots.

for m=0, n_bias-1 do begin
	sa_bias = bias_start + m* bias_step 
	page_label = vert_label + ' = ' + strtrim( string(sa_bias, format='(i)'), 2)
	for j=0, 7 do begin
        	plot, i_fb, av_vol(m,*,j), xtitle=horiz_label+i_units,$
		ytitle='Output Voltage' + v_units,$
		charsize=1, xstyle=1, /ynozero,$
		title=' Series Array Channel ' + strtrim( string( j, format='(I)'),2) $
		+ '    Card ' + card + '   peak-to-peak=' + string(estim_range(m,j))
		;Plot error bars if keyword set. Error bars are value +- stdev.
		if  keyword_set(errors) then errplot, ibias,$
		av_vol(i,*)-dev_vol(i,*), av_vol(i,*)+dev_vol(i,*)
	endfor
	xyouts, 0.0*(!D.X_SIZE), 1.00*(!D.Y_SIZE), full_name, /device   ;Print filename as title
	xyouts, 0.6*(!D.X_SIZE), 1.00*(!D.Y_SIZE), page_label, /device   ;Print SA_BIAS on title line
endfor     

close,3


;Merit function calculated from the peak-to-peak values
for chan=0,sav(3)-1 do begin
	plot,(bias_start+findgen(sav(1))*bias_step)/1000.,estim_range(*,chan),xtitle='sa_bias (/1000)',ytitle='peak-to-peak',charsize=1,$
	xstyle=1, /ynozero,title=' Series Array Channel '+strtrim( string( chan, format='(I)'),2)+ '    Card '+card
endfor

page_label = 'Merit function: peak-to-peak'
xyouts, 0.0*(!D.X_SIZE), 1.00*(!D.Y_SIZE), full_name, /device   ;Print filename as title
xyouts, 0.6*(!D.X_SIZE), 1.00*(!D.Y_SIZE), page_label, /device   ;Print SA_BIAS on title

device, /close                  ;close ps

;spawn,'ggv '+plot_file+' &'	;run the ggv to see the plot file (commented in the auto_setup version)

for chan=0,sav(3)-1 do begin		
	a=max(estim_range(*,chan),i)		;method: peak-to-peak
	ind(chan)=i(0)
endfor

print,''
print,'###########################################################################'
print,'SA bias and target (adc_offset) channel by channel:'
print,'###########################################################################'
for chan=0,7 do begin
	print,'Channel:',chan
	deriv_av_vol=smooth(deriv(i_fb,reform(av_vol(ind(chan),*,chan))),5)
	final_sa_bias_ch_by_ch(chan)=round(bias_start + ind(chan)* bias_step)
	print,'sa_bias @ step',ind(chan),', ie sa_bias=',final_sa_bias_ch_by_ch(chan)
;	min_point=min(av_vol(ind(chan),150:380,chan),ind_min)	;in case we want to lock on the negative slope
;	ind_min=150+ind_min

;	ind_pos_der=where(deriv_av_vol(0:ind_min-15) gt 0)
;	if n_elements(ind_pos_der) eq 1 then ind_pos_der=1
;	ind_max=max(ind_pos_der)

       min_point=min(av_vol(ind(chan),20:250,chan),ind_min)   ;in case we want to lock on the positive slope
       ind_min=20+ind_min
       ;print,ind_min
       ind_neg_der=where(deriv_av_vol(ind_min+10:399) lt 0)
       if n_elements(ind_neg_der) eq 1 then ind_neg_der=399
       ind_max=min(ind_neg_der)+ind_min+10
       ;print,ind_max
	;max_point=max(av_vol(ind(chan),ind_min-149:ind_min,chan),ind_max)	
        ;ind_max=max(ind_pos_der)

	;ind_max=ind_min-149+ind_max
	ind_half_point=round(0.5*(ind_min+ind_max))
	target_half_point_ch_by_ch(chan)=round(1000.*av_vol(ind(chan),ind_half_point,chan))
;Mikes new target selection
;	target_half_point_ch_by_ch(chan) = round(sa_middle(ind(chan),chan)*1000.)
	fb_half_point_ch_by_ch(chan)=round(1000.*i_fb(ind_half_point))
	;min_slope=min(deriv_av_vol(ind(chan),100:300,chan),indd)	
	;ind_min_slope=indd+100						
	;target_min_slope_ch_by_ch(chan)=round(1000.*av_vol(ind(chan),ind_min_slope,chan))
	print,'target  @ half point=',target_half_point_ch_by_ch(chan)
	;fb_min_slope_ch_by_ch(chan)=round(1000.*i_fb(ind_min_slope))
	print,'sa_fb   @ half point=',fb_half_point_ch_by_ch(chan)
	;print,' '

	print,'###########################################################################'
	;print,' '
;stop
endfor

;stop

SA_target=target_half_point_ch_by_ch
SA_fb_init=fb_half_point_ch_by_ch

;final_sa_bias_ch_by_ch(2)=66000		;for testing purposes
;SA_fb_init(3)=-5

for chan=0,7 do begin
	if (final_sa_bias_ch_by_ch(chan) gt 65535) or (final_sa_bias_ch_by_ch(chan) le 0) then begin
		final_sa_bias_ch_by_ch(chan)=0
		ind(chan)=0
		print,' '
		print,'###########################################################################'
		print,' '
		print,'WARNING: SA bias of channel'+string(chan)+' has been set to zero bacause' 
		print,'         the program found a non valid value'
		print,' '
		print,'###########################################################################'
	endif
	if (SA_fb_init(chan) gt 65535) or (SA_fb_init(chan) le 0) then begin
		SA_fb_init(chan)=32000
		print,' '
		print,'###########################################################################'
		print,' '
		print,'WARNING: SA fb of channel'+string(chan)+' found on the SA V-phi curve has' 
		print,'         been set to 32000 bacause the program found a non valid value'
		print,' '
		print,'###########################################################################'		
	endif
endfor

print,' '
print,'###########################################################################'
print,' '
print,'For details check '+string(plot_file)
print,' '
print,'###########################################################################'

file_name_sa_points=file_name+'_sa_points'
plot_file = folder + 'analysis/' + file_name_sa_points + '.ps'
print,' '
print,'###########################################################################'
print,' '
print,'To view the SA locking points check '+string(plot_file)
print,' '
print,'###########################################################################'
charsz=1
set_plot, 'ps'
device, filename= plot_file, /landscape
peak_to_peak=lonarr(8)
for j=0, 7 do begin
	m=ind(j)
	sa_bias = bias_start + m* bias_step 
       	plot, i_fb, av_vol(m,*,j), xtitle=horiz_label+i_units,$
	ytitle='Output Voltage' + v_units,$
	charsize=charsz, xstyle=1, /ynozero,$
	title=' SA Ch ' + strtrim( string( j, format='(I)'),2) $
	+ '   peak-to-peak=' + strcompress(string(round(estim_range(m,j))),/remove_all)$
	+ '   @ bias=' + strcompress(string(round(final_sa_bias_ch_by_ch(j))),/remove_all)
	oplot, [i_fb(0),i_fb(n_elements(i_fb)-1)],[SA_target(j),SA_target(j)]/1000.
	oplot, [SA_fb_init(j),SA_fb_init(j)]/1000.,[-200,200]
	peak_to_peak(j)=estim_range(m,j)
endfor
device,/close

;spawn,'scp '+plot_file+' act:act!now@lancelot:/home// '+plot_file+' 

if file_search('/misc/mce_plots',/test_directory) eq '/misc/mce_plots' then begin
        if file_search('/misc/mce_plots/'+ctime,/test_directory) ne '/misc/mce_plots/'+ctime $
                then spawn, 'mkdir /misc/mce_plots/'+ctime
        spawn, 'cp -rf '+plot_file+' /misc/mce_plots/'+ctime
        spawn, 'chgrp -R mceplots /misc/mce_plots/'+ctime
endif

if keyword_set(interactive) then spawn, 'ggv '+plot_file+' &'

theend:

end
