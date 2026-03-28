<?php
require 'utils.php';
$last_updated = null;
try {
    $last_updated = new DateTime(getData()['last_updated']);
    $last_updated = $last_updated->format('Y-m-d H:i');
} catch (Exception $e) {
    echo('Error parsing last_updated date: ' . $e->getMessage());
}


?>
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <link rel="stylesheet" href="css/style.css">
    <title>Jellyfin Leaderboard</title>
</head>
<body>
    <h1>Jellyfin Leaderboard</h1>
    <h2 class="last_updated">Last Updated: <?php echo $last_updated ?: 'Undefined'; ?></h2>
    <div class="tables-container">
        <div class="weekly-leaderboard-container leader-table">
            <table class="weekly-leaderboard">
                <tr>
                    <th colspan="4">Weekly Leaderboard</th>
                </tr>
                <tr>
                    <th>Username</th>
                    <th>Points</th>
                    <th>Watched Items</th>
                    <th>Watched Minutes</th>
                </tr>
                <?php foreach (getUsersByPointsWeekly() as $id => $user):?>
                <tr>
                    <td><a href="./user.php?id=<?=$id?>"><?php echo htmlspecialchars($user['name']); ?></a></td>
                    <td><?php echo htmlspecialchars($user['weekly_stats']['points']); ?></td>
                    <td><?php echo htmlspecialchars($user['weekly_stats']['items_completed']); ?></td>
                    <td><?php echo getHourMinuteString($user['weekly_stats']['watch_minutes']); ?></td>
                </tr>
                <?php endforeach; ?>
            </table>
        </div>
        <table class="leader-table">
            <tr>
                <th colspan="4">Daily Play Count</th>
            </tr>
            <tr>
                <th>Username</th>
                <th>Play Count</th>
                <th>Watched Minutes</th>
                <th>Streak</th>
            </tr>
            <?php foreach (getUsersByPlaycount() as $user):?>
                <tr>
                    <td><?php echo htmlspecialchars($user['name']); ?></td>
                    <td><?php echo htmlspecialchars($user['daily_stats']['items_completed']); ?></td>
                    <td><?php echo getHourMinuteString($user['daily_stats']['watch_minutes']); ?></td>
                    <td><?php echo $user['streak'] > 1 || $user['streak'] == 0 ? htmlspecialchars($user['streak']) . ' days' : htmlspecialchars($user['streak']) . ' day'; ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
        <table class="totals-table leader-table">
            <tr>
                <th colspan="3">Totals</th>
            </tr>
            <tr>
                <th>Username</th>
                <th>Total Points</th>
                <th>Total Watched Minutes</th>
            </tr>
            <?php foreach (getUsersByPoints() as $user): ?>
                <tr>
                    <td><?php echo htmlspecialchars($user['name']); ?></td>
                    <td><?php echo htmlspecialchars($user['points']); ?></td>
                    <td><?php echo getHourMinuteString($user['total_watchtime']); ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
        <table>
            <tr>
                <th colspan="3">Latest Activity</th>
            </tr>
            <tr>
                <th>Username</th>
                <th>Last Activity</th>
                <th>Last&nbsp;Active On</th>
            </tr>
            <?php foreach (getUsersByActivity() as $user):
                $last_activity = null;
                try {
                    $last_activity = new DateTime($user['last_activity']['date']);
                } catch (Exception $e) {

                }
                $last_activity = $last_activity->format('Y-m-d'); ?>
                <tr>
                    <td><?php echo htmlspecialchars($user['name']); ?></td>
                    <td><?php echo htmlspecialchars($user['last_activity']['name']); ?></td>
                    <td><span style="white-space:nowrap;"><?php echo htmlspecialchars($last_activity); ?></span></td>
                </tr>
            <?php endforeach; ?>
        </table>
    </div>
</body>
</html>