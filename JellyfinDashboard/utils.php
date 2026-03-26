<?php
function getHourMinuteString($minutes): string
{
    return floor($minutes / 60) . 'h ' . (int)$minutes % 60 . 'm';
}