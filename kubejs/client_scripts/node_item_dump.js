(function () {

    var TT_Minecraft = Java.loadClass('net.minecraft.client.Minecraft')

    var ttChestOpen = false
    var ttTicksOpen = 0
    var ttCopied = false

    console.info('[TechTreeDump] Client script loaded')

    ClientEvents.tick(function (event) {

        var mc = TT_Minecraft.getInstance()

        if (mc.player == null) {
            ttChestOpen = false
            ttTicksOpen = 0
            ttCopied = false
            return
        }

        var menu = mc.player.containerMenu

        if (menu == null) {
            ttChestOpen = false
            ttTicksOpen = 0
            ttCopied = false
            return
        }

        // InventoryMenu does not have getRowCount().
        // ChestMenu does.
        var rows = 0

        try {
            rows = menu.getRowCount()
        } catch (err) {
            ttChestOpen = false
            ttTicksOpen = 0
            ttCopied = false
            return
        }

        if (rows <= 0) {
            return
        }

        // Detect newly opened chest
        if (!ttChestOpen) {
            ttChestOpen = true
            ttTicksOpen = 0
            ttCopied = false
        }

        // Only copy once per chest opening
        if (ttCopied) {
            return
        }

        ttTicksOpen++

        // Wait for chest contents to sync
        if (ttTicksOpen < 10) {
            return
        }

        var chestSlots = rows * 9
        var itemIds = []
        var seenIds = {}

        var slot
        var ttStack
        var ttItemId

        for (slot = 0; slot < chestSlots; slot++) {

            ttStack = menu.getSlot(slot).getItem()

            if (!ttStack.isEmpty()) {

                ttItemId = String(ttStack.id)

                if (!seenIds[ttItemId]) {
                    seenIds[ttItemId] = true
                    itemIds.push(ttItemId)
                }
            }
        }

        if (itemIds.length === 0) {
            return
        }

        itemIds.sort()

        // Blank first line is intentional.
        // This makes Draw.io display:
        //
        // Unlocks:
        // <blank line>
        // item
        // item
        var clipboardText =
            '\n' +
            itemIds.join('\n')

        mc.keyboardHandler.setClipboard(clipboardText)

        ttCopied = true

        mc.player.displayClientMessage(
            Text.of(
                '[Tech Tree] Copied ' +
                itemIds.length +
                ' unique items to clipboard'
            ),
            false
        )

        console.info(
            '[TechTreeDump] Scanned ' +
            chestSlots +
            ' slots and copied ' +
            itemIds.length +
            ' unique items'
        )
    })

})();