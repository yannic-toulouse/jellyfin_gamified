<?php
require 'utils.php';
$user_data = getData();
$user_id = $_GET['id'];
$user = $user_data['users'][$user_id];
$rank = 0;
foreach (getUsersByPoints() as $key => $value) {
    $rank++;
    if($key == $_GET['id']) {
        break;
    }
}
?>
<!doctype html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <link rel="stylesheet" href="css/style.css">
    <title><?=htmlspecialchars($user['name'])?></title>
</head>
<body>
    <a href="./index.php"><h2><- Back</h2></a>
    <div class="tables-container">
        <div class="weekly-leaderboard-container leader-table">
            <table class="weekly-leaderboard">
                <tr>
                    <th colspan="3"><?=htmlspecialchars($user['name'])?></th>
                </tr>
                <tr>
                    <th>Points</th>
                    <th>Watched Minutes</th>
                    <th>Streak</th>
                </tr>
                    <tr>
                        <td><?php echo htmlspecialchars($user['points']); ?></td>
                        <td><?php echo getHourMinuteString($user['total_watchtime']); ?></td>
                        <td><?php echo $user['streak']; echo $user['streak'] != 1 ? ' days' : ' day'; ?></td>
                    </tr>
            </table>
        </div>
        <div class="weekly-leaderboard-container leader-table">
            <table class="weekly-leaderboard">
                <tr>
                    <th colspan="3">Last Watched</th>
                </tr>
                <tr>
                    <td><img src="<?= htmlspecialchars($user['last_activity']['images']['thumb']) ?>" alt=""></td>
                </tr>
                <tr>
                    <td><?= htmlspecialchars($user['last_activity']['name']) ?></td>
                </tr>
            </table>
        </div>
    </div>
</body>
</html>
