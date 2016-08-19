#!/bin/bash
#在打包目录自动对设备进行升级

CNONE='\033[00m' #\033[01;00m
CRED='\033[01;31m'
CGREEN='\033[01;32m'
CYELLOW='\033[01;33m'
CBLUE='\033[01;34m'
CPURPLE='\033[01;35m'
CCYAN='\033[01;36m'
CWHITE='\033[01;37m'
C0=$CNONE

PASSWORD=adminsangfornetwork
USERNAME=root

VERSION=4.0.00_B
VERSION_NAME="${VERSION_TITLE}${VERSION}(`date +%Y%m%d`)";
PKG_NAME="${VERSION_NAME}.dev";
USB_NAME="${VERSION_NAME}.iso"
SIG_NAME="${VERSION_NAME}.pkg"
REVISION_NAME="${VERSION_NAME}.svn"

PKG_DIR=${BUILDDIR}/pkg/;
USB_DIR=${BUILDDIR}/usb/;

PKG_BAK_NAME="vmp`date +%m%d`.dev";
SIG_BAK_NAME="vmp`date +%m%d`.pkg"
USB_BAK_NAME="${VERSION_TITLE}`date +%m%d`.iso";

PKG_FILENAME=${PKG_DIR}${PKG_NAME};
USB_FILENAME=${USB_DIR}${USB_NAME};
SIG_FILENAME=${PKG_DIR}${SIG_NAME};
PKG_BAK_FILENAME=${PKG_DIR}${PKG_BAK_NAME};
USB_BAK_FILENAME=${USB_DIR}${USB_BAK_NAME};

IP="200.200.103.94,200.200.103.95"
#REPLACE_PKGNAME="vtp`date +%m%d`"
#REPLACE_PKGPATH=${PKG_DIR}
LOG_NAME=auto_update_log.txt
is_rm=0
is_upload=0
upload_dir=
is_ou=0;

alliso_path=""
oldiso_path=""
newiso_path=""

PACKAGE_IP="200.200.1.6"
VMPVERSION="VMP4.0"

# 打印帮助信息
usage()
{
cat << HELP
	-f,--filename				update filename
	-i,--ip				update ip [ip1,ip2,ip3,....]
	-a,--aip			add ip
	-r,--rm				rm -f /boot/fireware/current/runtime/cfg
	-u,					upload 200.200.0.3
	-o,					only upload 200.200.0.3,not update
    -p                  password
	-c [oldiso_path|newiso_path]    compare old iso and new iso   
						default:FILENAME="VMP${VERSION}(`date +%Y%m%d`)".pkg;
						ip="200.200.103.1,200.200.103.3,200.200.103.5,200.200.103.7,200.200.103.9"							
HELP
	exit 1;
}

#打印错误代码并退出
die()
{
	ecode=$1;
	shift;	
	echo -e "${CRED}$*, exit $ecode${C0}" | tee -a $LOG_NAME;
	exit $ecode;
}
#[ $#  -lt 2 ] && usage

#解析参数
param_parse()
{
	# 可输入的选项参数设置
	ARGS=`getopt -a -o ruof:i:a:p: -l filename:,ip:,aip:,rm -- "$@"`
	[ $? -ne 0 ] && usage

	eval set -- "${ARGS}"
	while true
	do
		case "$1" in
		-f|--filename)
			PKG_FILENAME="$2";
			shift
			;;
		-i|--ip)
			IP="$2"
			shift
			;;
		-a|--aip)
			IP="$IP,$2"
			#echo $IP
			shift
			;;
		-h|--help)
			usage
			;;  
		-r|--rm)
			is_rm=1
			;;
		-u)
			is_upload=1
			;;
		-o)
			is_ou=1
			;;
        -p)
           PASSWORD="$2"
           shift
           ;;
		 -c)
			alliso_path="$2"
			shift
			;;
		--)
			shift  
			break
			;;  
			esac  
	shift
	done
}

#处理ip格式，比如200.200.103.1/3/5/7;或者200.200.103.1-3；
deal_ip()
{
	local ip_arrays
	for iptemp in `echo $IP | sed 's/,/ /g'`
	do
		local ip_seg1=`echo "$iptemp" | awk -F "." '{print $1}'`
		local ip_seg2=`echo "$iptemp" | awk -F "." '{print $2}'`
		local ip_seg3=`echo "$iptemp" | awk -F "." '{print $3}'`
		local ip_seg4=`echo "$iptemp" | awk -F "." '{print $4}'`
		
		for i in `echo $ip_seg4 | sed 's/\// /g'`
		do
			declare -a seg_ip4
			k=0
			for j in `echo $i | sed 's/-/ /g'`
			do
				seg_ip4[k]=$j
				k=$(($k+1))
			done
			if [ ${#seg_ip4[@]} -eq 2 ]; then
				for ((m=${seg_ip4[0]};m<=${seg_ip4[1]};m++))
				do 
					ip_one=$(printf "%s.%s.%s.%s" "$ip_seg1" "$ip_seg2" "$ip_seg3" "$m")
					ip_arrays="$ip_arrays $ip_one"
				done
			elif [ ${#seg_ip4[@]} -eq 1 ]; then
				ip_one=$(printf "%s.%s.%s.%s" "$ip_seg1" "$ip_seg2" "$ip_seg3" "${seg_ip4[0]}")
				ip_arrays="$ip_arrays $ip_one"
			fi
		done
	done
	IP=$ip_arrays
}

#对设备升级
update_device()
{
	echo -e "${CGREEN}[auto_update] update_device START ...${C0}" | tee -a $LOG_NAME
	[ ! -f $PKG_FILENAME ] && die 2 "$PKG_FILENAME is not a valid file!"
	cp -f $PKG_FILENAME vmp.dev
	iparr=`echo $IP | sed 's/,/ /g'`
	echo "IP = [$iparr]" | tee -a $LOG_NAME
	for iptem in $iparr
	do
		iptem=`echo $iptem | sed 's/ //g'`
		
		echo -e "auto_update device ${iptem} ${CGREEN}step 1:upload ${PKG_FILENAME}...${C0}" | tee -a $LOG_NAME
		sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" vmp.dev ${USERNAME}@${iptem}:/sf/ | tee -a $LOG_NAME
		if [ $? -ne 0 ]; then
			echo -e "${CRED}auto_update device ${iptem} step 1:upload ${PKG_FILENAME} FAILED!${C0}" | tee -a $LOG_NAME
			continue
		fi
		
		echo -e "auto_update device ${iptem} ${CGREEN}step 2: update from pkg...${C0}" | tee -a $LOG_NAME
		if [ $is_rm -eq 1 ];then
			sshpass -p ${PASSWORD} ssh -p 22 -o "StrictHostKeyChecking no" ${USERNAME}@${iptem} "cd /sf;chmod u+x vmp.dev;\
				./vmp.dev -icp sangfor.vt@201314;if [ $? -eq 0 ];then rm -f /boot/firmware/current/runtime/cfg;\
				reboot;else echo update fail;fi" | tee -a $LOG_NAME
			if [ $? -ne 0 ]; then
				echo -e "${CREAD}auto_update device ${iptem} step 2:update from pkg FAILED!${C0}" | tee -a $LOG_NAME
				continue
			fi
		else
			sshpass -p ${PASSWORD} ssh -p 22 -o "StrictHostKeyChecking no" ${USERNAME}@${iptem} "cd /sf;chmod u+x vmp.dev;lasterr=0;\
				./vmp.dev -icp sangfor.vt@201314;lasterr=\$?;if [ \$lasterr -eq 0 ];then echo \"rebooting\"; reboot;else echo update fail\(\$lasterr\);fi" | tee -a $LOG_NAME
			if [ $? -ne 0 ]; then
				echo -e "${CREAD}auto_update device ${iptem} step 2:update from pkg FAILED!${C0}" | tee -a $LOG_NAME
				continue
			fi
		fi
	done
}

#上传包的方法
upload_package_ssh()
{
	if [ $is_upload -eq 1 ];then
		echo -e "${CGREEN}upload pkg and iso to ${PACKAGE_IP} ...${C0}" | tee -a $LOG_NAME
			#upload pkg and iso to 200.200.0.3
		if [ ! -f $PKG_FILENAME ]; then
			echo -e "$PKG_FILENAME is not a valid file!"
			[ ! -f $PKG_BAK_FILENAME ] && die 2 "$PKG_FILENAME and $PKG_BAK_FILENAME are not a valid file!"
			PKG_FILENAME=$PKG_BAK_FILENAME
		#else
			#mv $PKG_FILENAME $PKG_BAK_FILENAME
			#[ $? -ne 0 ] && die 3 "mv $PKG_FILENAME to $PKG_BAK_FILENAME failed!"
		fi
		
		if [ ! -f $USB_FILENAME ]; then
			echo -e "$USB_FILENAME is not a valid file!"
			[ ! -f $USB_BAK_FILENAME ] && die 2 "$USB_FILENAME and $USB_BAK_FILENAME are not a valid file!"
			USB_FILENAME=$USB_BAK_FILENAME
		#else
		#	mv $USB_FILENAME $USB_BAK_FILENAME
		#	[ $? -ne 0 ] && die 4 "mv $USB_FILENAME to $USB_BAK_FILENAME failed!"
		fi
		
		if [ ! -f $SIG_FILENAME ]; then
			die 2 "$SIG_FILENAME is not a valid file!"
		fi
		
		if [ `date +%p` = "AM" ];then
			smb_cmd="cd VT;cd ${VMPVERSION};mkdir `date +%Y-%m-%d`(上午,研发用);quit" 
			upload_path="\\${PACKAGE_IP}\\研发包提交文件夹\\VT\\${VMPVERSION}\\`date +%Y-%m-%d`(上午,研发用)"
		else
			smb_cmd="cd VT;cd ${VMPVERSION};mkdir `date +%Y-%m-%d`(下午,研发用);quit" 
			upload_path="\\${PACKAGE_IP}\\研发包提交文件夹\\VT\\${VMPVERSION}\\`date +%Y-%m-%d`(下午,研发用)"
		fi
		smbclient //${PACKAGE_IP}/研发包提交文件夹 -U develop%develop -c "${smb_cmd}"
		[ $? -ne 0 ] && die 6 "smbclient mkdir dir pkg and iso failed!"
		
		echo -e "${CGREEN}smbclient mkdir success...${C0}"
		echo -e "$upload_path"
		old_dir=`pwd`
		cd $PKG_DIR
		echo -e "${CGREEN}upload pkg to ${PACKAGE_IP} start...${C0}"
		sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" $PKG_NAME ${USERNAME}@200.200.100.53:"$upload_path" | tee -a $LOG_NAME
		[ $? -ne 0 ] && die 6 "scp upload pkg failed!"
		echo -e "${CGREEN}upload pkg to ${PACKAGE_IP} success...${C0}"
		
		echo -e "${CGREEN}upload $SIG_NAME to ${PACKAGE_IP} start...${C0}"
		sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" $SIG_NAME ${USERNAME}@200.200.100.53:"$upload_path" | tee -a $LOG_NAME
		[ $? -ne 0 ] && die 6 "scp upload $SIG_NAME failed!"
		echo -e "${CGREEN}upload $SIG_NAME to ${PACKAGE_IP} end...${C0}"
		
		cd $USB_DIR
		echo -e "${CGREEN}upload iso to ${PACKAGE_IP} start...${C0}"
		sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" $USB_NAME ${USERNAME}@200.200.100.53:"$upload_path" | tee -a $LOG_NAME
		[ $? -ne 0 ] && die 6 "scp upload iso failed!"
		sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" $REVISION_NAME ${USERNAME}@200.200.100.53:"$upload_path" | tee -a $LOG_NAME
		echo -e "${CGREEN}upload iso to ${PACKAGE_IP} end...${C0}"
		
		cd $old_dir;
		#对比iso的不同
		if [ x"$alliso_path" != x"" ]; then
			oldiso_path=`echo $alliso_path | awk -F "|" '{print $1}'`
			newiso_path=`echo $alliso_path | awk -F "|" '{print $2}'`
			old_revision=`echo $alliso_path | awk -F "|" '{print $3}'`
			new_revision=`echo $alliso_path | awk -F "|" '{print $4}'`
			[ ! -e "$oldiso_path" -o ! -e "newiso_path" ] && return
			chmod u+x buildreport.sh
			./buildreport.sh "$oldiso_path" "$newiso_path" "$old_revision" "$new_revision"
			[ $? -ne 0 ] && echo -e "${CRED}compare $oldiso_path $newiso_path failed!" && return
			if [ -f "compare_result.txt" ]; then
				sshpass -p ${PASSWORD} scp -P 22 -o "StrictHostKeyChecking no" compare_result.txt ${USERNAME}@200.200.100.53:"$upload_path" | tee -a $LOG_NAME
				[ $? -ne 0 ] && die 6 "scp upload compare_result.txt failed!"
				echo -e "${CGREEN}upload compare_result.txt to ${PACKAGE_IP} success...${C0}"
			fi
		fi
	fi
}

upload_0_3()
{
	if [ $is_upload -eq 1 ];then
		echo -e "${CGREEN}upload pkg and iso to 200.200.0.3 ...${C0}" | tee -a $LOG_NAME
			#upload pkg and iso to 200.200.0.3
		[ ! -f $PKG_FILENAME ] && die 2 "$PKG_FILENAME is not a valid file!"
		mv $PKG_FILENAME $PKG_BAK_FILENAME
		[ $? -ne 0 ] && die 3 "mv $PKG_FILENAME to $PKG_BAK_FILENAME failed!"
		
		[ ! -f $USB_FILENAME ] && die 2 "$USB_FILENAME is not a valid file!"
		mv $USB_FILENAME $USB_BAK_FILENAME
		[ $? -ne 0 ] && die 4 "mv $USB_FILENAME to $USB_BAK_FILENAME failed!"
		
		if [ `date +%p` = "AM" ];then
			date_dir="`date +%Y-%m-%d`(上午,研发用)"
		else
			date_dir="`date +%Y-%m-%d`(下午,研发用)"
		fi
		
		old_path=`pwd`
		[ -f "200.200.0.3/VT/VTP1.2" ] && die 7 " 200.200.0.3/VT/VTP1.2 dir not exist!"
		cd 200.200.0.3/VT/VTP1.2
		mkdir $date_dir
		[ $? -ne 0 ] && die 5 " mkdir $datedir fail!"
		cd $old_path
		
		echo -e "${CGREEN}upload pkg to 200.200.0.3 start...${C0}"
		cp $PKG_BAK_FILENAME "200.200.0.3/VT/VTP1.2/$date_dir"
		[ $? -ne 0 ] && die 6 "cp $PKG_BAK_FILENAME to 200.200.0.3/VT/VTP1.2/$date_dir fail!"
		echo -e "${CGREEN}upload pkg to 200.200.0.3 success...${C0}"
		
		echo -e "${CGREEN}upload iso to 200.200.0.3 start...${C0}"
		cp $USB_BAK_FILENAME "200.200.0.3/VT/VTP1.2/$date_dir"
		[ $? -ne 0 ] && die 6 "cp $USB_BAK_FILENAME to 200.200.0.3/VT/VTP1.2/$date_dir fail!"
		echo -e "${CGREEN}upload iso to 200.200.0.3 end...${C0}"
	fi
}
main()
{
	mount /dev/pts
	param_parse $*
	deal_ip
	if [ $is_ou -ne 1 ]; then
		update_device
	fi
	
	upload_package_ssh
	rm -fv vmp.dev
}

main $*
exit 0

