<?php
require 'utils.php';
$user_data = file_get_contents('../data/users.json');
$user_data = json_decode($user_data, true);
$user_id = $_GET['id'];
$user = $user_data['users'][$user_id];
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
    <h1><?=htmlspecialchars($user['name'])?></h1>
    <div class="tables-container">
        <table>
            <tr>
                <td><?=htmlspecialchars($user['points'])?> points</td>
            </tr>
            <tr>
                <td><?=getHourMinuteString($user['total_watchtime'])?></td>
            </tr>
        </table>
    </div>
</body>
</html>
