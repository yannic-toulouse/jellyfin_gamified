<?php
function getData()
{
    $data = file_get_contents('../data/users.json');
    return json_decode($data, true);
}

function getUsers()
{
    return getData()['users'];
}

function getUsersByPoints()
{
    $users_by_points = getUsers();
    uasort($users_by_points, function ($a, $b) {
        return $b['points'] <=> $a['points'];
    });
    return $users_by_points;
}

function getUsersByPointsWeekly()
{
    $users_by_points_weekly = getUsers();
    uasort($users_by_points_weekly, function ($a, $b) {
        return $b['weekly_stats']['points'] <=> $a['weekly_stats']['points'];
    });
    return $users_by_points_weekly;
}

function getUsersByPlaycount()
{
    $users_by_playcount = getUsers();
    uasort($users_by_playcount, function ($a, $b) {
        return $b['daily_stats']['items_completed'] <=> $a['daily_stats']['items_completed'];
    });
    return $users_by_playcount;
}

function getUsersByActivity()
{
    $users_by_activity = getUsers();
    uasort($users_by_activity, function ($a, $b) {
        return $b['last_activity'] <=> $a['last_activity'];
    });
    return $users_by_activity;
}

function getHourMinuteString($minutes): string
{
    return floor($minutes / 60) . 'h ' . (int)$minutes % 60 . 'm';
}