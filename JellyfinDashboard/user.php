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

$monthly_points_data = [];
foreach ($user['monthly_totals'][date('Y')] as $month => $value) {
    $monthly_points_data[] = [
            'y' => $value['points'],
            'label' => DateTime::createFromFormat('!m', $month)->format('F')
    ];
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
    <a href="./index.php">&larr; Back</a>
    <h1><?=htmlspecialchars($user['name'])?></h1>
    <div class="tables-container">
        <table>
            <tr class="header-row">
                <th>Rank</th>
                <th>Points</th>
                <th>Watched Minutes</th>
                <th>Streak</th>
            </tr>
                <tr>
                    <td>#<?= $rank ?></td>
                    <td><?php echo htmlspecialchars($user['points']); ?></td>
                    <td><?php echo getHourMinuteString($user['total_watchtime']); ?></td>
                    <td><?php echo $user['streak']; echo $user['streak'] != 1 ? ' days' : ' day'; ?></td>
                </tr>
        </table>
        <div class="tables-container">
            <table style="width: 40vw">
                <tr class="header-row">
                    <th colspan="3">Last Watched</th>
                </tr>
                <tr>
                    <td><img src="<?= htmlspecialchars($user['last_activity']['images']['thumb']) ?>" alt="<?=htmlspecialchars($user['last_activity']['name'])?> thumbnail" style="width: 100%"></td>
                </tr>
                <tr>
                    <td><?= htmlspecialchars($user['last_activity']['name']) ?></td>
                </tr>
            </table>
            <table>
                <tr class="header-row">
                    <th>Point History YTD</th>
                </tr>
                <tr style="height: 100%">
                    <td><div id="chartContainer" style="height: 500px; width: 100%"></div></td>
                </tr>
            </table>
        </div>
    </div>

    <script src="https://cdn.canvasjs.com/canvasjs.min.js"></script>
    <script>
        window.onload = function () {

            const chart = new CanvasJS.Chart("chartContainer", {
                axisY: {
                    title: "Points"
                },
                data: [{
                    <?php if(sizeof($monthly_points_data) > 1):?>
                        type: "line",
                    <?php else:?>
                        type: "column",
                    <?php endif; ?>
                    dataPoints: <?php echo json_encode($monthly_points_data, JSON_NUMERIC_CHECK); ?>
                }]
            });
            chart.render();

        }
    </script>
</body>
</html>
