<?php
$user_data = file_get_contents('../data/users.json');
$users = json_decode($user_data, true);
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
    <div class="tables-container">
        <table>
            <tr>
                <th colspan="3">Daily Play Count</th>
            </tr>
            <tr>
                <th>Username</th>
                <th>Play Count</th>
                <th>Played minutes</th>
            </tr>
            <?php foreach ($users as $user): ?>
                <tr>
                    <td><?php echo htmlspecialchars($user['name']); ?></td>
                    <td><?php echo htmlspecialchars($user['daily_stats']['items_completed']); ?></td>
                    <td><?php echo htmlspecialchars(round($user['daily_stats']['watch_minutes'], 0)); ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
        <table>
            <tr>
                <th colspan="2">Total Points</th>
            </tr>
            <tr>
                <th>Username</th>
                <th>Total Points</th>
            </tr>
            <?php foreach ($users as $user): ?>
                <tr>
                    <td><?php echo htmlspecialchars($user['name']); ?></td>
                    <td><?php echo htmlspecialchars($user['points']); ?></td>
                </tr>
            <?php endforeach; ?>
        </table>
    </div>
</body>