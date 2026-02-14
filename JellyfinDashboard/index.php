<?php
$user_data = file_get_contents('../data/users.json');
$data = json_decode($user_data, true);
$users = $data['users'];
$last_updated = null;
try {
    $last_updated = new DateTime($data['last_updated']);
    $last_updated = $last_updated->format('Y-m-d H:i');
} catch (Exception $e) {
    echo('Error parsing last_updated date: ' . $e->getMessage());
}

$users_by_points = uasort($users, function ($a, $b) {
    return $b['points'] <=> $a['points'];
});

$users_by_playcount = uasort($users, function ($a, $b) {
    return $b['daily_stats']['items_completed'] <=> $a['daily_stats']['items_completed'];
});
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
    <h2 class="last_updated">Last Updated: <?php echo $last_updated ? $last_updated : 'Undefined'; ?></h2>
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