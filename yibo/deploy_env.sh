#!/bin/bash -e

#重置环境并重新部署

ENV_NAME=$1
FUELIP=172.17.0.70
if [ $# -gt 1 ] && [ -n "$2" ]; then
	FUELIP=$2
fi
if [ -z "$ENV_NAME" -o -z "$FUELIP" ]; then
	echo no environment name or fuel ip $ENV_NAME $FUELIP
	exit 1
fi

echo "start at $(date), FUELIP=$FUELIP, ENV_NAME=$ENV_NAME"

FUEL_CMD="ssh $FUELIP FUELCLIENT_CUSTOM_SETTINGS=/etc/fuel/client/config.yaml fuel"

#根据环境名称找出环境ID
if [ -z "$ENV_ID" ]; then
	LST=$($FUEL_CMD environment --list | grep -E '^[0-9]+' | \
	  awk -F'|' '{print "ID="$1";NAME=\""$3"\""}' | \
	  sed 's/ //g')
	for line in $LST; do
		eval $line
		#echo $ID $NAME
		if [ "$NAME" = "$ENV_NAME" ]; then
			ENV_ID=$ID
		fi
	done
fi

if [ -z "$ENV_ID" ]; then
	echo no environment id
	exit 1
fi

echo "ENV_ID=$ENV_ID"

function get_env_status()
{
	local env_id=$1
	LST=$($FUEL_CMD environment --env $env_id | grep -E '^[0-9]+' | \
	  awk -F'|' '{print "ID="$1";NAME=\""$3"\";STATUS="$2}' | \
	  sed 's/ //g')
	for line in $LST; do
		eval $line
		echo $STATUS
		break
	done
}

function is_all_nodes_online()
{
	local env_id=$1
	LST=$($FUEL_CMD node --env $env_id list | grep -E '^[0-9]+' | \
	  awk -F'|' '{print "ID="$1";STATUS="$2";NAME=\""$3"\";ONLINE="$9}' | \
	  sed 's/ //g')
	for line in $LST; do
		eval $line
		#echo $line
		if [ "$ONLINE" != "True" ]; then
			return 1
		fi
		if [ "$STATUS" != "discover" ]; then
			return 2
		fi
	done
}

function wait_env_status()
{
	local env_id=$1
	local want_status=$2
	local wait_count=$3
	while [ $wait_count -gt 0 ]; do
		local STATUS=$(get_env_status $env_id)
		if [ "$STATUS" = "$want_status" ]; then
            echo "ok, status of env($env_id) is $want_status now"
			return 0
		fi
        echo "status of env($env_id) is $STATUS, but $want_status is expected, left time $((wait_count*5)) seconds."
		let wait_count--
		sleep 5
	done
	echo wait time out
	return 1
}

#如果环境的状态不是new则重置之
STATUS=$(get_env_status $ENV_ID)
if [ "$STATUS" != "new" ]; then
	#重置环境
    echo "reset env $ENV_ID"
	$FUEL_CMD reset --env $ENV_ID
fi

#等环境的状态变成 new，最多等一个小时
echo "$(date) wait env status change to new..."
WAIT_COUNT=$((60*60/5))
wait_env_status $ENV_ID new $WAIT_COUNT

#等待所有结点上线，最多等一个小时
WAIT_COUNT=$((60*60/5))
while [ $WAIT_COUNT -gt 0 ]; do
	if is_all_nodes_online $ENV_ID; then
        echo "$(date) now all nodes are on line"
		break
	fi
    echo "$(date) wait all nodes to be online, left time $((WAIT_COUNT*5)) seconds." 
	let WAIT_COUNT--
	sleep 5
done

#部署 fuel deploy-changes，该命令是同步的
echo "$(date) deploy-changes --env $ENV_ID"
$FUEL_CMD deploy-changes --env $ENV_ID

#等环境部署完成，最多等5分钟
WAIT_COUNT=$((5*60/5))
wait_env_status $ENV_ID operational $WAIT_COUNT

echo "done at $(date)"
